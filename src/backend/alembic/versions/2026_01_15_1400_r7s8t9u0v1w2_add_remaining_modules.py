"""Add remaining modules MOD-13 to MOD-21

Revision ID: r7s8t9u0v1w2
Revises: q6r7s8t9u0v1
Create Date: 2026-01-15 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'r7s8t9u0v1w2'
down_revision = 'q6r7s8t9u0v1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============ MOD-13: Supply Chain Advanced ============

    # Warehouses
    op.create_table('warehouses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('warehouse_type', sa.String(50), nullable=False),
        sa.Column('address_line1', sa.String(500), nullable=False),
        sa.Column('address_line2', sa.String(500), nullable=True),
        sa.Column('city', sa.String(100), nullable=False),
        sa.Column('state', sa.String(100), nullable=False),
        sa.Column('country', sa.String(100), nullable=False, server_default='India'),
        sa.Column('pincode', sa.String(20), nullable=False),
        sa.Column('contact_person', sa.String(200), nullable=True),
        sa.Column('contact_phone', sa.String(20), nullable=True),
        sa.Column('contact_email', sa.String(255), nullable=True),
        sa.Column('total_area_sqft', sa.Integer(), nullable=True),
        sa.Column('usable_area_sqft', sa.Integer(), nullable=True),
        sa.Column('max_capacity_units', sa.Integer(), nullable=True),
        sa.Column('gstin', sa.String(20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Bin Locations
    op.create_table('bin_locations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('zone', sa.String(50), nullable=True),
        sa.Column('aisle', sa.String(50), nullable=True),
        sa.Column('rack', sa.String(50), nullable=True),
        sa.Column('shelf', sa.String(50), nullable=True),
        sa.Column('bin', sa.String(50), nullable=True),
        sa.Column('max_weight_kg', sa.Integer(), nullable=True),
        sa.Column('max_volume_cbm', sa.Numeric(10, 3), nullable=True),
        sa.Column('max_units', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Warehouse Stock
    op.create_table('warehouse_stocks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('item_code', sa.String(100), nullable=False),
        sa.Column('item_name', sa.String(500), nullable=False),
        sa.Column('bin_location_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reserved_qty', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('available_qty', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('unit_of_measure', sa.String(50), nullable=False),
        sa.Column('batch_number', sa.String(100), nullable=True),
        sa.Column('serial_numbers', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('unit_cost', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('total_value', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('last_count_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id']),
        sa.ForeignKeyConstraint(['bin_location_id'], ['bin_locations.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Stock Transfers
    op.create_table('stock_transfers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transfer_number', sa.String(50), nullable=False, unique=True),
        sa.Column('from_warehouse_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('to_warehouse_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='draft'),
        sa.Column('transfer_date', sa.Date(), nullable=False),
        sa.Column('expected_arrival', sa.Date(), nullable=True),
        sa.Column('actual_arrival', sa.Date(), nullable=True),
        sa.Column('transport_mode', sa.String(100), nullable=True),
        sa.Column('vehicle_number', sa.String(50), nullable=True),
        sa.Column('driver_name', sa.String(200), nullable=True),
        sa.Column('driver_phone', sa.String(20), nullable=True),
        sa.Column('tracking_number', sa.String(100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('received_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['from_warehouse_id'], ['warehouses.id']),
        sa.ForeignKeyConstraint(['to_warehouse_id'], ['warehouses.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Stock Transfer Items
    op.create_table('stock_transfer_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transfer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('item_code', sa.String(100), nullable=False),
        sa.Column('item_name', sa.String(500), nullable=False),
        sa.Column('quantity_requested', sa.Integer(), nullable=False),
        sa.Column('quantity_shipped', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('quantity_received', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('unit_of_measure', sa.String(50), nullable=False),
        sa.Column('batch_number', sa.String(100), nullable=True),
        sa.Column('from_bin_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('to_bin_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('unit_cost', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['transfer_id'], ['stock_transfers.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Suppliers
    op.create_table('suppliers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(500), nullable=False),
        sa.Column('display_name', sa.String(200), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending_approval'),
        sa.Column('tier', sa.String(50), nullable=False, server_default='approved'),
        sa.Column('contact_person', sa.String(200), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('website', sa.String(500), nullable=True),
        sa.Column('address_line1', sa.String(500), nullable=True),
        sa.Column('address_line2', sa.String(500), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('country', sa.String(100), nullable=False, server_default='India'),
        sa.Column('pincode', sa.String(20), nullable=True),
        sa.Column('gstin', sa.String(20), nullable=True),
        sa.Column('pan', sa.String(20), nullable=True),
        sa.Column('tan', sa.String(20), nullable=True),
        sa.Column('msme_number', sa.String(50), nullable=True),
        sa.Column('msme_type', sa.String(50), nullable=True),
        sa.Column('bank_name', sa.String(200), nullable=True),
        sa.Column('bank_account', sa.String(50), nullable=True),
        sa.Column('bank_ifsc', sa.String(20), nullable=True),
        sa.Column('payment_terms_days', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('credit_limit', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('currency', sa.String(10), nullable=False, server_default='INR'),
        sa.Column('categories', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Supplier Scorecards
    op.create_table('supplier_scorecards',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('supplier_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('evaluation_period', sa.String(50), nullable=False),
        sa.Column('evaluation_date', sa.Date(), nullable=False),
        sa.Column('quality_score', sa.Numeric(5, 2), nullable=False, server_default='0'),
        sa.Column('delivery_score', sa.Numeric(5, 2), nullable=False, server_default='0'),
        sa.Column('price_score', sa.Numeric(5, 2), nullable=False, server_default='0'),
        sa.Column('service_score', sa.Numeric(5, 2), nullable=False, server_default='0'),
        sa.Column('compliance_score', sa.Numeric(5, 2), nullable=False, server_default='0'),
        sa.Column('overall_score', sa.Numeric(5, 2), nullable=False, server_default='0'),
        sa.Column('orders_placed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('orders_on_time', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('orders_complete', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('defect_rate_ppm', sa.Numeric(10, 2), nullable=False, server_default='0'),
        sa.Column('total_spend', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('evaluated_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id']),
        sa.ForeignKeyConstraint(['evaluated_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Reorder Rules
    op.create_table('reorder_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('item_code', sa.String(100), nullable=False),
        sa.Column('item_name', sa.String(500), nullable=False),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reorder_method', sa.String(50), nullable=False),
        sa.Column('min_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reorder_point', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reorder_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('safety_stock', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('lead_time_days', sa.Integer(), nullable=False, server_default='7'),
        sa.Column('preferred_supplier_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('auto_create_po', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_triggered', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id']),
        sa.ForeignKeyConstraint(['preferred_supplier_id'], ['suppliers.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Purchase Forecasts
    op.create_table('purchase_forecasts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('item_code', sa.String(100), nullable=False),
        sa.Column('item_name', sa.String(500), nullable=False),
        sa.Column('forecast_period', sa.String(50), nullable=False),
        sa.Column('forecast_date', sa.Date(), nullable=False),
        sa.Column('forecast_method', sa.String(50), nullable=False),
        sa.Column('forecasted_demand', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('actual_demand', sa.Integer(), nullable=True),
        sa.Column('variance', sa.Numeric(10, 2), nullable=True),
        sa.Column('variance_percent', sa.Numeric(5, 2), nullable=True),
        sa.Column('confidence_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('historical_periods', sa.Integer(), nullable=False, server_default='12'),
        sa.Column('generated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('generated_by', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Goods Receipts
    op.create_table('goods_receipts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('receipt_number', sa.String(50), nullable=False, unique=True),
        sa.Column('receipt_date', sa.Date(), nullable=False),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('supplier_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('purchase_order_number', sa.String(50), nullable=True),
        sa.Column('invoice_number', sa.String(50), nullable=True),
        sa.Column('challan_number', sa.String(50), nullable=True),
        sa.Column('vehicle_number', sa.String(50), nullable=True),
        sa.Column('transporter_name', sa.String(200), nullable=True),
        sa.Column('lr_number', sa.String(50), nullable=True),
        sa.Column('total_items', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_value', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('received_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('inspected_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id']),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id']),
        sa.ForeignKeyConstraint(['received_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Goods Receipt Items
    op.create_table('goods_receipt_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('receipt_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('item_code', sa.String(100), nullable=False),
        sa.Column('item_name', sa.String(500), nullable=False),
        sa.Column('quantity_ordered', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('quantity_received', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('quantity_accepted', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('quantity_rejected', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('unit_of_measure', sa.String(50), nullable=False),
        sa.Column('unit_price', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('total_value', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('batch_number', sa.String(100), nullable=True),
        sa.Column('serial_numbers', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('bin_location_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('inspection_status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['receipt_id'], ['goods_receipts.id']),
        sa.ForeignKeyConstraint(['bin_location_id'], ['bin_locations.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # ============ MOD-14: E-commerce & POS ============

    # Product Categories
    op.create_table('product_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('slug', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image_url', sa.String(1000), nullable=True),
        sa.Column('icon', sa.String(100), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('meta_title', sa.String(200), nullable=True),
        sa.Column('meta_description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['parent_id'], ['product_categories.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Products
    op.create_table('products',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('sku', sa.String(100), nullable=False, unique=True),
        sa.Column('name', sa.String(500), nullable=False),
        sa.Column('slug', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('short_description', sa.String(500), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='draft'),
        sa.Column('base_price', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('sale_price', sa.Numeric(15, 2), nullable=True),
        sa.Column('cost_price', sa.Numeric(15, 2), nullable=True),
        sa.Column('mrp', sa.Numeric(15, 2), nullable=True),
        sa.Column('hsn_code', sa.String(20), nullable=True),
        sa.Column('gst_rate', sa.Numeric(5, 2), nullable=False, server_default='18'),
        sa.Column('is_tax_inclusive', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('track_inventory', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('stock_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('low_stock_threshold', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('allow_backorder', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('weight_kg', sa.Numeric(10, 3), nullable=True),
        sa.Column('length_cm', sa.Numeric(10, 2), nullable=True),
        sa.Column('width_cm', sa.Numeric(10, 2), nullable=True),
        sa.Column('height_cm', sa.Numeric(10, 2), nullable=True),
        sa.Column('images', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('thumbnail_url', sa.String(1000), nullable=True),
        sa.Column('video_url', sa.String(1000), nullable=True),
        sa.Column('brand', sa.String(200), nullable=True),
        sa.Column('manufacturer', sa.String(200), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('attributes', postgresql.JSON(), nullable=True),
        sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_new', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_bestseller', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_digital', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('meta_title', sa.String(200), nullable=True),
        sa.Column('meta_description', sa.Text(), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('sold_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rating_avg', sa.Numeric(3, 2), nullable=False, server_default='0'),
        sa.Column('review_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['category_id'], ['product_categories.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Product Variants
    op.create_table('product_variants',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sku', sa.String(100), nullable=False, unique=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('attributes', postgresql.JSON(), nullable=False),
        sa.Column('price', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('sale_price', sa.Numeric(15, 2), nullable=True),
        sa.Column('cost_price', sa.Numeric(15, 2), nullable=True),
        sa.Column('stock_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('barcode', sa.String(100), nullable=True),
        sa.Column('image_url', sa.String(1000), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Shopping Carts
    op.create_table('shopping_carts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('session_id', sa.String(100), nullable=True),
        sa.Column('subtotal', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('discount_amount', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('tax_amount', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('shipping_amount', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('total', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('coupon_code', sa.String(50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Cart Items
    op.create_table('cart_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('cart_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('variant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('unit_price', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('total_price', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['cart_id'], ['shopping_carts.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.ForeignKeyConstraint(['variant_id'], ['product_variants.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Online Orders
    op.create_table('online_orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_number', sa.String(50), nullable=False, unique=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('payment_status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('subtotal', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('discount_amount', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('tax_amount', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('shipping_amount', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('total_amount', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('amount_paid', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('currency', sa.String(10), nullable=False, server_default='INR'),
        sa.Column('customer_name', sa.String(200), nullable=False),
        sa.Column('customer_email', sa.String(255), nullable=False),
        sa.Column('customer_phone', sa.String(20), nullable=False),
        sa.Column('billing_address', sa.Text(), nullable=False),
        sa.Column('billing_city', sa.String(100), nullable=False),
        sa.Column('billing_state', sa.String(100), nullable=False),
        sa.Column('billing_pincode', sa.String(20), nullable=False),
        sa.Column('billing_country', sa.String(100), nullable=False, server_default='India'),
        sa.Column('shipping_address', sa.Text(), nullable=False),
        sa.Column('shipping_city', sa.String(100), nullable=False),
        sa.Column('shipping_state', sa.String(100), nullable=False),
        sa.Column('shipping_pincode', sa.String(20), nullable=False),
        sa.Column('shipping_country', sa.String(100), nullable=False, server_default='India'),
        sa.Column('shipping_method', sa.String(100), nullable=True),
        sa.Column('tracking_number', sa.String(100), nullable=True),
        sa.Column('shipped_at', sa.DateTime(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('payment_gateway', sa.String(100), nullable=True),
        sa.Column('transaction_id', sa.String(200), nullable=True),
        sa.Column('coupon_code', sa.String(50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('internal_notes', sa.Text(), nullable=True),
        sa.Column('confirmed_at', sa.DateTime(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),
        sa.Column('cancel_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Online Order Items
    op.create_table('online_order_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('variant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('sku', sa.String(100), nullable=False),
        sa.Column('name', sa.String(500), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('unit_price', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('discount_amount', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('tax_amount', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('total_price', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('quantity_shipped', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('quantity_returned', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['order_id'], ['online_orders.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.ForeignKeyConstraint(['variant_id'], ['product_variants.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # POS Terminals
    op.create_table('pos_terminals',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('terminal_code', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('location', sa.String(200), nullable=True),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='offline'),
        sa.Column('device_id', sa.String(100), nullable=True),
        sa.Column('printer_ip', sa.String(50), nullable=True),
        sa.Column('cash_drawer_connected', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('barcode_scanner_connected', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('default_tax_rate', sa.Numeric(5, 2), nullable=False, server_default='18'),
        sa.Column('allow_discount', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('max_discount_percent', sa.Numeric(5, 2), nullable=False, server_default='20'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_sync', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # POS Transactions
    op.create_table('pos_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('terminal_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('invoice_number', sa.String(50), nullable=False, unique=True),
        sa.Column('transaction_date', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('customer_name', sa.String(200), nullable=True),
        sa.Column('customer_phone', sa.String(20), nullable=True),
        sa.Column('customer_email', sa.String(255), nullable=True),
        sa.Column('subtotal', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('discount_amount', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('discount_percent', sa.Numeric(5, 2), nullable=False, server_default='0'),
        sa.Column('tax_amount', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('total_amount', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('round_off', sa.Numeric(5, 2), nullable=False, server_default='0'),
        sa.Column('payment_method', sa.String(50), nullable=False),
        sa.Column('amount_tendered', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('change_given', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('transaction_ref', sa.String(200), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='completed'),
        sa.Column('cashier_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['terminal_id'], ['pos_terminals.id']),
        sa.ForeignKeyConstraint(['cashier_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # POS Transaction Items
    op.create_table('pos_transaction_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('variant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('sku', sa.String(100), nullable=False),
        sa.Column('name', sa.String(500), nullable=False),
        sa.Column('barcode', sa.String(100), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('unit_price', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('discount_amount', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('tax_rate', sa.Numeric(5, 2), nullable=False, server_default='0'),
        sa.Column('tax_amount', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('total_price', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['transaction_id'], ['pos_transactions.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.ForeignKeyConstraint(['variant_id'], ['product_variants.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Loyalty Programs
    op.create_table('loyalty_programs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('points_per_rupee', sa.Numeric(10, 4), nullable=False, server_default='1'),
        sa.Column('min_purchase_for_points', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('points_value_rupees', sa.Numeric(10, 4), nullable=False, server_default='0.01'),
        sa.Column('min_points_redeem', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('max_redemption_percent', sa.Numeric(5, 2), nullable=False, server_default='50'),
        sa.Column('points_expiry_days', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Loyalty Points
    op.create_table('loyalty_points',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('program_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('customer_phone', sa.String(20), nullable=False),
        sa.Column('customer_name', sa.String(200), nullable=True),
        sa.Column('customer_email', sa.String(255), nullable=True),
        sa.Column('total_earned', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_redeemed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('current_balance', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('tier', sa.String(50), nullable=False, server_default='bronze'),
        sa.Column('last_earned_at', sa.DateTime(), nullable=True),
        sa.Column('last_redeemed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['program_id'], ['loyalty_programs.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Loyalty Transactions
    op.create_table('loyalty_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('loyalty_points_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transaction_type', sa.String(50), nullable=False),
        sa.Column('points', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('balance_after', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('pos_transaction_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['loyalty_points_id'], ['loyalty_points.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('ix_warehouses_company_id', 'warehouses', ['company_id'])
    op.create_index('ix_suppliers_company_id', 'suppliers', ['company_id'])
    op.create_index('ix_products_company_id', 'products', ['company_id'])
    op.create_index('ix_products_sku', 'products', ['sku'])
    op.create_index('ix_online_orders_company_id', 'online_orders', ['company_id'])
    op.create_index('ix_online_orders_order_number', 'online_orders', ['order_number'])
    op.create_index('ix_pos_transactions_company_id', 'pos_transactions', ['company_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_pos_transactions_company_id')
    op.drop_index('ix_online_orders_order_number')
    op.drop_index('ix_online_orders_company_id')
    op.drop_index('ix_products_sku')
    op.drop_index('ix_products_company_id')
    op.drop_index('ix_suppliers_company_id')
    op.drop_index('ix_warehouses_company_id')

    # Drop tables in reverse order
    op.drop_table('loyalty_transactions')
    op.drop_table('loyalty_points')
    op.drop_table('loyalty_programs')
    op.drop_table('pos_transaction_items')
    op.drop_table('pos_transactions')
    op.drop_table('pos_terminals')
    op.drop_table('online_order_items')
    op.drop_table('online_orders')
    op.drop_table('cart_items')
    op.drop_table('shopping_carts')
    op.drop_table('product_variants')
    op.drop_table('products')
    op.drop_table('product_categories')
    op.drop_table('goods_receipt_items')
    op.drop_table('goods_receipts')
    op.drop_table('purchase_forecasts')
    op.drop_table('reorder_rules')
    op.drop_table('supplier_scorecards')
    op.drop_table('suppliers')
    op.drop_table('stock_transfer_items')
    op.drop_table('stock_transfers')
    op.drop_table('warehouse_stocks')
    op.drop_table('bin_locations')
    op.drop_table('warehouses')
