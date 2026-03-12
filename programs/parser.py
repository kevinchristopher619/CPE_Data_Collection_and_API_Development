import xml.etree.ElementTree as ET
import json
from database import create_db, insert_cpes_batch, truncate_cpes

XML_FILE = r'D:\securin\SVCE _ Securin Labs _ Assessment\official-cpe-dictionary_v2\official-cpe-dictionary_v2.xml'

def parse_cpe_xml_efficient(file_path):
    count = 0
    batch = []
    BATCH_SIZE = 10000  
    
    # Official NVD Namespaces
    ns = {
        'cpe': 'http://cpe.mitre.org/dictionary/2.0',
        'cpe23': 'http://scap.nist.gov/schema/cpe-extension/2.3'
    }
    
    context = ET.iterparse(file_path, events=('end',))
    
    for event, elem in context:
        if elem.tag == '{http://cpe.mitre.org/dictionary/2.0}cpe-item':
            try:
                # 1. Title
                title = elem.find('cpe:title', ns)
                title_text = title.text if title is not None else "Unknown"
                
                # 2. CPE URIs
                cpe22_uri = elem.get('name')
                cpe23 = elem.find('cpe23:cpe23-item', ns)
                cpe23_uri = cpe23.get('name') if cpe23 is not None else None
                
                # 3. References
                refs = []
                refs_elem = elem.find('cpe:references', ns)
                if refs_elem is not None:
                    for ref in refs_elem.findall('cpe:reference', ns):
                        href = ref.get('href')
                        if href:
                            refs.append(href)
                ref_json = json.dumps(refs) if refs else None
                
                # 4. Deprecation Dates - CORRECTED
                cpe22_depr_date = None
                cpe23_depr_date = None
                
                # CPE 2.2 deprecation: check 'deprecation_date' attribute on cpe-item tag
                cpe22_depr_date = elem.get('deprecation_date')
                
                # CPE 2.3 deprecation: look inside cpe-23:cpe23-item for <cpe-23:deprecation> element
                if cpe23 is not None:
                    depr_elem = cpe23.find('cpe23:deprecation', ns)
                    if depr_elem is not None:
                        cpe23_depr_date = depr_elem.get('date')
                
                # 5. Append data tuple to batch
                batch.append((
                    title_text[:500], 
                    ref_json, 
                    cpe22_uri, 
                    cpe23_uri, 
                    cpe22_depr_date, 
                    cpe23_depr_date
                ))
                count += 1
                
                # Execute batch insert when full
                if len(batch) >= BATCH_SIZE:
                    insert_cpes_batch(batch)
                    print(f"Parsed and inserted {count} CPEs...")
                    batch.clear()
                    
            except Exception as e:
                print(f"Error parsing item: {e}")
                continue
            finally:
                # Clear element from memory to prevent RAM crash
                elem.clear()

    # Insert any remaining records
    if batch:
        insert_cpes_batch(batch)
        print(f"Parsed and inserted {count} CPEs...")
        
    print(f"✓ Total CPEs successfully imported: {count}")

if __name__ == "__main__":
    parse_cpe_xml_efficient(XML_FILE)