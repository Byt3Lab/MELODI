import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from core.application import Application
from modules.melodi_invoice.models import Invoice, InvoiceItem

def test_invoice_module():
    print("Initializing Application...")
    app = Application()
    app.build()
    app.db.create_all()
    
    print("Checking if module is loaded...")
    # Check if router is registered
    # Note: This depends on how routers are stored. 
    # app.server.app.url_map should contain /invoice
    
    has_invoice_route = False
    for rule in app.server.app.url_map.iter_rules():
        if "invoice" in str(rule):
            has_invoice_route = True
            break
    
    if has_invoice_route:
        print("SUCCESS: Invoice routes found.")
    else:
        print("FAILURE: Invoice routes NOT found.")
        sys.exit(1)

    print("Checking database models...")
    session = app.db.get_session()
    try:
        # Try to query the table (it should be empty but exist)
        invoices = session.query(Invoice).all()
        print(f"SUCCESS: Invoice table exists. Count: {len(invoices)}")
        
        # Create a dummy invoice
        inv = Invoice(customer_name="Test Client", total=100.0)
        session.add(inv)
        session.commit()
        print("SUCCESS: Created test invoice.")
        
        # Clean up
        session.delete(inv)
        session.commit()
        print("SUCCESS: Cleaned up test invoice.")
        
    except Exception as e:
        print(f"FAILURE: Database error: {e}")
        sys.exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    test_invoice_module()
