import xmlrpc.client
from config import ODOO_URL, DB, USERNAME, PASSWORD

# Connect to Odoo
common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})

models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

def get_quotation_stats(email):
    # Step 1: Find partner
    partner_ids = models.execute_kw(
        DB, uid, PASSWORD,
        'res.partner', 'search',
        [[['email', '=', email]]]
    )

    if not partner_ids:
        return {
            "total": 0,
            "pending": 0,
            "completed": 0
        }

    partner_id = partner_ids[0]

    # Step 2: Get quotations (sale.order)
    orders = models.execute_kw(
        DB, uid, PASSWORD,
        'sale.order', 'search_read',
        [[['partner_id', '=', partner_id]]],
        {'fields': ['state']}
    )

    # Step 3: Count
    total = len(orders)
    pending = len([o for o in orders if o['state'] in ['draft', 'sent']])
    completed = len([o for o in orders if o['state'] == 'sale'])

    return {
        "total": total,
        "pending": pending,
        "completed": completed
    }
    
def create_portal_user(name, email):
    # Step 1: Check if partner already exists
    partner_ids = models.execute_kw(
        DB, uid, PASSWORD,
        'res.partner', 'search',
        [[['email', '=', email]]]
    )

    if partner_ids:
        partner_id = partner_ids[0]
    else:
        # Create partner
        partner_id = models.execute_kw(
            DB, uid, PASSWORD,
            'res.partner', 'create',
            [{
                'name': name,
                'email': email,
                'customer_rank': 1
            }]
        )

    # Step 2: Check if user already exists
    user_ids = models.execute_kw(
        DB, uid, PASSWORD,
        'res.users', 'search',
        [[['login', '=', email]]]
    )

    if user_ids:
        return {"message": "User already exists", "user_id": user_ids[0]}

    # Step 3: Get Portal Group ID
    portal_group_id = models.execute_kw(
        DB, uid, PASSWORD,
        'res.groups', 'search',
        [[['name', '=', 'Portal']]]
    )[0]

    # Step 4: Create user
    user_id = models.execute_kw(
        DB, uid, PASSWORD,
        'res.users', 'create',
        [{
            'name': name,
            'login': email,
            'partner_id': partner_id,
            'groups_id': [(6, 0, [portal_group_id])]
        }]
    )

    # Step 5: Send reset password email
    models.execute_kw(
        DB, uid, PASSWORD,
        'res.users', 'action_reset_password',
        [[user_id]]
    )

    return {
        "message": "Portal user created successfully",
        "user_id": user_id
    }