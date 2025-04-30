import gradio as gr
import pandas as pd
from data_utils import fetch_sheet_data, process_stock_data, process_orders_data, process_supplier_data
from visuals import (
    create_inventory_value_chart, create_stock_level_chart, create_low_stock_chart,
    create_sales_by_product_chart, create_sales_by_client_chart, create_sales_by_source_chart,
    create_order_status_chart, create_payment_status_chart, create_suppliers_by_amount_chart,
    create_supplier_payment_status_chart, generate_inventory_summary, generate_sales_summary,
    generate_supplier_summary, filter_data_by_date, create_sales_by_city_chart
)
from ai_assistant import handle_user_query
from datetime import datetime, timedelta
import json
from io import StringIO

# Define color scheme
PRIMARY_COLOR = "#3F51B5"  # Blue color (replacing orange)

def process_sheet(sheet_url):
    """Process the sheet and display results."""
    # Fetch data from each sheet
    stock_status, stock_df = fetch_sheet_data(sheet_url, "Stock")
    commandes_status, commandes_df = fetch_sheet_data(sheet_url, "Commandes")
    fournisseur_status, fournisseur_df = fetch_sheet_data(sheet_url, "Fournisseur")
    
    # Check if we successfully fetched at least one sheet
    if stock_df is None and commandes_df is None and fournisseur_df is None:
        error_html = """
        <div style="padding: 15px; background-color: #FFEBEE; margin-bottom: 20px;">
            <h3 style="margin: 0; color: #C62828;">Erreur de Connexion</h3>
            <p style="margin: 5px 0 0; color: #D32F2F;">Impossible de récupérer des données. Vérifiez l'URL et les noms des feuilles.</p>
        </div>
        """
        return (
            error_html, 
            None, 
            gr.update(visible=False), 
            None, None, None, None,
            None, None, None, None, None, None, None,
            None, None, None,
            datetime.now().strftime("%Y-%m-%d"),
            datetime.now().strftime("%Y-%m-%d"),
            datetime.now().strftime("%Y-%m-%d"),
            datetime.now().strftime("%Y-%m-%d")
        )
    
    # Process data for each sheet if available
    if stock_df is not None:
        processed_stock_df = process_stock_data(stock_df)
        
        # Add a fallback price if not present (for inventory value calculation)
        if 'Prix' not in processed_stock_df.columns and 'Prix produit' in processed_stock_df.columns:
            processed_stock_df['Prix'] = pd.to_numeric(processed_stock_df['Prix produit'], errors='coerce').fillna(0)
        elif 'Prix' not in processed_stock_df.columns:
            # If no price column exists, add a default one (all 1 for simplicity)
            processed_stock_df['Prix'] = 1.0
            
        stock_json = processed_stock_df.to_json(orient='split') if processed_stock_df is not None else None
        inventory_value_chart = create_inventory_value_chart(processed_stock_df)
        stock_level_chart = create_stock_level_chart(processed_stock_df)
        low_stock_chart = create_low_stock_chart(processed_stock_df)
        inventory_summary = generate_inventory_summary(processed_stock_df)
    else:
        stock_json = None
        inventory_value_chart = None
        stock_level_chart = None
        low_stock_chart = None
        inventory_summary = ""
    
    # Process orders data
    if commandes_df is not None:
        processed_commandes_df = process_orders_data(commandes_df)
        
        # Convert datetime columns to string before JSON serialization to avoid timestamp issues
        date_cols = [col for col in processed_commandes_df.columns if 'date' in col.lower()]
        for col in date_cols:
            if col in processed_commandes_df.columns and pd.api.types.is_datetime64_any_dtype(processed_commandes_df[col]):
                # Store dates as ISO format strings - this makes them easy to parse later
                processed_commandes_df[col] = processed_commandes_df[col].dt.strftime('%Y-%m-%d')
                print(f"Converted {col} to string format for JSON serialization: {processed_commandes_df[col].head().tolist()}")
                
        # Print sample dates for debugging
        for col in date_cols:
            if col in processed_commandes_df.columns:
                print(f"Commandes - {col} samples after processing: {processed_commandes_df[col].head().tolist()}")
        
        commandes_json = processed_commandes_df.to_json(orient='split') if processed_commandes_df is not None else None
        sales_by_product_chart = create_sales_by_product_chart(processed_commandes_df)
        sales_by_client_chart = create_sales_by_client_chart(processed_commandes_df)
        sales_by_source_chart = create_sales_by_source_chart(processed_commandes_df)
        sales_by_city_chart = create_sales_by_city_chart(processed_commandes_df)
        order_status_chart = create_order_status_chart(processed_commandes_df)
        payment_status_chart = create_payment_status_chart(processed_commandes_df)
        sales_summary = generate_sales_summary(processed_commandes_df)
    else:
        commandes_json = None
        sales_by_product_chart = None
        sales_by_client_chart = None
        sales_by_source_chart = None
        sales_by_city_chart = None
        order_status_chart = None
        payment_status_chart = None
        sales_summary = ""
    
    # Process supplier data
    if fournisseur_df is not None:
        processed_fournisseur_df = process_supplier_data(fournisseur_df)
        
        # Convert datetime columns to string before JSON serialization to avoid timestamp issues
        date_cols = [col for col in processed_fournisseur_df.columns if 'date' in col.lower()]
        for col in date_cols:
            if col in processed_fournisseur_df.columns and pd.api.types.is_datetime64_any_dtype(processed_fournisseur_df[col]):
                # Store dates as ISO format strings - this makes them easy to parse later
                processed_fournisseur_df[col] = processed_fournisseur_df[col].dt.strftime('%Y-%m-%d')
                print(f"Converted {col} to string format for JSON serialization: {processed_fournisseur_df[col].head().tolist()}")
                
        # Print sample dates for debugging
        for col in date_cols:
            if col in processed_fournisseur_df.columns:
                print(f"Fournisseur - {col} samples after processing: {processed_fournisseur_df[col].head().tolist()}")
        
        fournisseur_json = processed_fournisseur_df.to_json(orient='split') if processed_fournisseur_df is not None else None
        suppliers_by_amount_chart = create_suppliers_by_amount_chart(processed_fournisseur_df)
        supplier_payment_status_chart = create_supplier_payment_status_chart(processed_fournisseur_df)
        supplier_summary = generate_supplier_summary(processed_fournisseur_df)
    else:
        fournisseur_json = None
        suppliers_by_amount_chart = None
        supplier_payment_status_chart = None
        supplier_summary = ""
    
    # Combine data for AI assistant
    combined_data_json = {
        "stock": stock_json,
        "commandes": commandes_json,
        "fournisseur": fournisseur_json
    }
    # Fix for FutureWarning by using json.dumps first
    combined_data_json = json.dumps(combined_data_json)
    
    # Get date ranges for the date filter (if date columns exist)
    start_date = None
    end_date = None
    
    # Try to extract date range from commandes and fournisseur DataFrames before date column conversion
    if commandes_df is not None:
        # Look for date columns
        date_cols = [col for col in processed_commandes_df.columns if 'date' in col.lower()]
        for date_col in date_cols:
            try:
                # Get min and max dates
                min_date = processed_commandes_df[date_col].min()
                max_date = processed_commandes_df[date_col].max()
                
                # Convert to datetime if they're strings now
                if isinstance(min_date, str):
                    min_date = pd.to_datetime(min_date)
                if isinstance(max_date, str):
                    max_date = pd.to_datetime(max_date)
                
                if pd.notna(min_date) and (start_date is None or min_date < start_date):
                    start_date = min_date
                
                if pd.notna(max_date) and (end_date is None or max_date > end_date):
                    end_date = max_date
            except Exception as e:
                print(f"Error extracting date range from commandes.{date_col}: {str(e)}")
                continue
    
    if fournisseur_df is not None:
        # Look for date columns
        date_cols = [col for col in processed_fournisseur_df.columns if 'date' in col.lower()]
        for date_col in date_cols:
            try:
                # Get min and max dates
                min_date = processed_fournisseur_df[date_col].min()
                max_date = processed_fournisseur_df[date_col].max()
                
                # Convert to datetime if they're strings now
                if isinstance(min_date, str):
                    min_date = pd.to_datetime(min_date)
                if isinstance(max_date, str):
                    max_date = pd.to_datetime(max_date)
                
                if pd.notna(min_date) and (start_date is None or min_date < start_date):
                    start_date = min_date
                
                if pd.notna(max_date) and (end_date is None or max_date > end_date):
                    end_date = max_date
            except Exception as e:
                print(f"Error extracting date range from fournisseur.{date_col}: {str(e)}")
                continue
    
    # Format dates for the date picker
    start_date_str = start_date.strftime("%Y-%m-%d") if start_date is not None else (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d") if end_date is not None else datetime.now().strftime("%Y-%m-%d")
    
    # Display success message
    success_html = """
    <div style="padding: 15px; background-color: #E8F5E9; margin-bottom: 20px;">
        <h3 style="margin: 0; color: #2E7D32;">Connexion Réussie!</h3>
        <p style="margin: 5px 0 0; color: #388E3C;">Données récupérées avec succès!</p>
    </div>
    """
    
    # Return all the data and visualizations
    return (
        success_html, 
        combined_data_json, 
        gr.update(visible=True), 
        inventory_value_chart, 
        stock_level_chart, 
        low_stock_chart, 
        inventory_summary,
        sales_by_product_chart, 
        sales_by_client_chart, 
        sales_by_source_chart, 
        sales_by_city_chart,
        order_status_chart, 
        payment_status_chart, 
        sales_summary,
        suppliers_by_amount_chart, 
        supplier_payment_status_chart, 
        supplier_summary,
        start_date_str,
        end_date_str,
        start_date_str,
        end_date_str
    )

def update_sales_dashboard_with_date_filter(combined_data_json, start_date, end_date):
    """Update sales dashboard with date filter."""
    try:
        # Print debugging information
        print(f"Filtering sales data from {start_date} to {end_date}")
        
        # Fix FutureWarning by wrapping the JSON string in StringIO
        from io import StringIO
        import json
        
        # Convert JSON back to dictionary of DataFrames
        combined_data = json.loads(combined_data_json)
        
        # Initialize variables for return values
        sales_by_product_chart = None
        sales_by_client_chart = None
        sales_by_source_chart = None
        sales_by_city_chart = None
        order_status_chart = None
        payment_status_chart = None
        sales_summary = ""
        
        # Update Orders charts and summary
        if "commandes" in combined_data and combined_data["commandes"]:
            # Properly parse the JSON with date_format specified
            commandes_df = pd.read_json(StringIO(combined_data["commandes"]), orient='split')
            
            # Print columns for debugging
            print("Commandes columns:", commandes_df.columns.tolist())
            
            # Check for date columns and convert to datetime if they're strings
            date_cols = [col for col in commandes_df.columns if 'date' in col.lower()]
            for col in date_cols:
                if col in commandes_df.columns:
                    # Print data type and sample values
                    print(f"Column {col} type: {commandes_df[col].dtype}")
                    print(f"Sample values for {col}: {commandes_df[col].head().tolist()}")
                    
                    # If the column is string type (which it should be from our serialization), convert to datetime
                    if pd.api.types.is_string_dtype(commandes_df[col]):
                        commandes_df[col] = pd.to_datetime(commandes_df[col], errors='coerce')
                        print(f"Converted string dates to datetime for {col}: {commandes_df[col].head().tolist()}")
            
            # Use "Date de commande" as the date column if it exists
            date_column = 'Date de commande'
            
            # Check if the date column exists, if not, try to find another date column
            if date_column not in commandes_df.columns:
                # Try to find a similar column
                date_cols = [col for col in commandes_df.columns if 'date' in col.lower()]
                if date_cols:
                    date_column = date_cols[0]
                    print(f"Using alternative date column for commandes: {date_column}")
            
            if date_column in commandes_df.columns:
                # Apply date filter directly
                try:
                    start_date_dt = pd.to_datetime(start_date)
                    end_date_dt = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
                    
                    print(f"Filtering commandes from {start_date_dt} to {end_date_dt}")
                    print(f"Sample dates before filtering: {commandes_df[date_column].head()}")
                    
                    # Filter the dataframe directly
                    filtered_commandes_df = commandes_df[
                        (commandes_df[date_column] >= start_date_dt) & 
                        (commandes_df[date_column] <= end_date_dt)
                    ]
                    
                    # If we filtered out all data, return the original data
                    if filtered_commandes_df.empty:
                        print("WARNING: All commandes data filtered out, returning original data")
                        filtered_commandes_df = commandes_df
                    
                    print(f"Filtered commandes data: {len(filtered_commandes_df)} rows (original: {len(commandes_df)} rows)")
                except Exception as e:
                    print(f"Error filtering commandes data: {str(e)}")
                    filtered_commandes_df = commandes_df
                
                # Generate charts with filtered data
                sales_by_product_chart = create_sales_by_product_chart(filtered_commandes_df)
                sales_by_client_chart = create_sales_by_client_chart(filtered_commandes_df)
                sales_by_source_chart = create_sales_by_source_chart(filtered_commandes_df)
                sales_by_city_chart = create_sales_by_city_chart(filtered_commandes_df)
                order_status_chart = create_order_status_chart(filtered_commandes_df)
                payment_status_chart = create_payment_status_chart(filtered_commandes_df)
                sales_summary = generate_sales_summary(filtered_commandes_df)
            else:
                print("No suitable date column found in commandes data")
                # Use original data if no date column is found
                sales_by_product_chart = create_sales_by_product_chart(commandes_df)
                sales_by_client_chart = create_sales_by_client_chart(commandes_df)
                sales_by_source_chart = create_sales_by_source_chart(commandes_df)
                sales_by_city_chart = create_sales_by_city_chart(commandes_df)
                order_status_chart = create_order_status_chart(commandes_df)
                payment_status_chart = create_payment_status_chart(commandes_df)
                sales_summary = generate_sales_summary(commandes_df)
        
        return (
            sales_by_product_chart, 
            sales_by_client_chart, 
            sales_by_source_chart,
            sales_by_city_chart, 
            order_status_chart, 
            payment_status_chart, 
            sales_summary
        )
    except Exception as e:
        error_message = """
        <div style="padding: 15px; background-color: #FFEBEE; margin-bottom: 20px;">
            <h3 style="margin: 0; color: #C62828;">Erreur de Filtrage</h3>
            <p style="margin: 5px 0 0; color: #D32F2F;">Erreur de mise à jour du tableau de bord des ventes: {}</p>
        </div>
        """.format(str(e))
        print(f"Error in sales date filtering: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None, None, None, None, None, error_message

def update_suppliers_dashboard_with_date_filter(combined_data_json, start_date, end_date):
    """Update suppliers dashboard with date filter."""
    try:
        # Print debugging information
        print(f"Filtering suppliers data from {start_date} to {end_date}")
        
        # Fix FutureWarning by wrapping the JSON string in StringIO
        from io import StringIO
        import json
        
        # Convert JSON back to dictionary of DataFrames
        combined_data = json.loads(combined_data_json)
        
        # Initialize variables for return values
        suppliers_by_amount_chart = None
        supplier_payment_status_chart = None
        supplier_summary = ""
        
        # Update Suppliers charts and summary
        if "fournisseur" in combined_data and combined_data["fournisseur"]:
            # Properly parse the JSON with date_format specified
            fournisseur_df = pd.read_json(StringIO(combined_data["fournisseur"]), orient='split')
            
            # Print columns for debugging
            print("Fournisseur columns:", fournisseur_df.columns.tolist())
            
            # Check for date columns and convert to datetime if they're strings
            date_cols = [col for col in fournisseur_df.columns if 'date' in col.lower()]
            for col in date_cols:
                if col in fournisseur_df.columns:
                    # Print data type and sample values
                    print(f"Column {col} type: {fournisseur_df[col].dtype}")
                    print(f"Sample values for {col}: {fournisseur_df[col].head().tolist()}")
                    
                    # If the column is string type (which it should be from our serialization), convert to datetime
                    if pd.api.types.is_string_dtype(fournisseur_df[col]):
                        fournisseur_df[col] = pd.to_datetime(fournisseur_df[col], errors='coerce')
                        print(f"Converted string dates to datetime for {col}: {fournisseur_df[col].head().tolist()}")
            
            # Use "Date de commande" as the date column if it exists
            date_column = 'Date de commande'
            
            # Check if the date column exists, if not, try to find another date column
            if date_column not in fournisseur_df.columns:
                # Try to find a similar column
                date_cols = [col for col in fournisseur_df.columns if 'date' in col.lower()]
                if date_cols:
                    date_column = date_cols[0]
                    print(f"Using alternative date column for fournisseurs: {date_column}")
            
            if date_column in fournisseur_df.columns:
                # Apply date filter directly
                try:
                    start_date_dt = pd.to_datetime(start_date)
                    end_date_dt = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
                    
                    print(f"Filtering fournisseurs from {start_date_dt} to {end_date_dt}")
                    print(f"Sample dates before filtering: {fournisseur_df[date_column].head()}")
                    
                    # Filter the dataframe directly
                    filtered_fournisseur_df = fournisseur_df[
                        (fournisseur_df[date_column] >= start_date_dt) & 
                        (fournisseur_df[date_column] <= end_date_dt)
                    ]
                    
                    # If we filtered out all data, return the original data
                    if filtered_fournisseur_df.empty:
                        print("WARNING: All fournisseur data filtered out, returning original data")
                        filtered_fournisseur_df = fournisseur_df
                    
                    print(f"Filtered fournisseur data: {len(filtered_fournisseur_df)} rows (original: {len(fournisseur_df)} rows)")
                except Exception as e:
                    print(f"Error filtering fournisseur data: {str(e)}")
                    filtered_fournisseur_df = fournisseur_df
                
                # Generate charts with filtered data
                suppliers_by_amount_chart = create_suppliers_by_amount_chart(filtered_fournisseur_df)
                supplier_payment_status_chart = create_supplier_payment_status_chart(filtered_fournisseur_df)
                supplier_summary = generate_supplier_summary(filtered_fournisseur_df)
            else:
                print("No suitable date column found in fournisseur data")
                # Use original data if no date column is found
                suppliers_by_amount_chart = create_suppliers_by_amount_chart(fournisseur_df)
                supplier_payment_status_chart = create_supplier_payment_status_chart(fournisseur_df)
                supplier_summary = generate_supplier_summary(fournisseur_df)
        
        return (
            suppliers_by_amount_chart, 
            supplier_payment_status_chart, 
            supplier_summary
        )
    except Exception as e:
        error_message = """
        <div style="padding: 15px; background-color: #FFEBEE; margin-bottom: 20px;">
            <h3 style="margin: 0; color: #C62828;">Erreur de Filtrage</h3>
            <p style="margin: 5px 0 0; color: #D32F2F;">Erreur de mise à jour du tableau de bord des fournisseurs: {}</p>
        </div>
        """.format(str(e))
        print(f"Error in suppliers date filtering: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None, error_message

# --- Create the Gradio Interface ---
with gr.Blocks(title="Gestionnaire d'Inventaire E-commerce", css="""
    /* Override default Gradio styles */
    .primary-button {
        background-color: #3F51B5 !important; /* Blue */
        border-color: #3F51B5 !important;
    }
    .primary-button:hover {
        background-color: #303F9F !important; /* Darker blue */
        border-color: #303F9F !important;
    }
    /* Style for selected tab */
    .tab-selected {
        border-color: #3F51B5 !important;
        color: #3F51B5 !important;
    }
    /* Tab hover effect */
    .tab-button:hover {
        background-color: rgba(63, 81, 181, 0.1) !important;
    }
    /* Style for filter buttons */
    .filter-button {
        background-color: #3F51B5 !important;
        color: white !important;
    }
""") as app:
    # Store data as JSON for later use
    combined_data_json = gr.State()
    
    # Welcome section
    with gr.Row():
        with gr.Column():
            gr.Markdown(
                """
                # 📊 Gestionnaire d'Inventaire E-commerce
                """
            )
    
    # Connection section
    with gr.Row():
        with gr.Column():
            sheet_url_input = gr.Textbox(
                label="URL Google Sheet", 
                placeholder="https://docs.google.com/spreadsheets/d/your-sheet-id/edit"
            )
            connect_button = gr.Button("Connecter", variant="primary", elem_classes=["primary-button"])
    
    # Status message area
    status_html = gr.HTML()
    
    # Dashboard section (initially hidden)
    dashboard_section = gr.Column(visible=False)
    
    with dashboard_section:
        # Create tabs for different dashboards
        with gr.Tabs() as tabs:
            # Inventory Dashboard Tab - NO DATE FILTER HERE
            with gr.TabItem("Tableau de Bord Inventaire", elem_classes=["tab-button"]):
                # Inventory Summary section
                gr.Markdown("### Résumé d'Inventaire")
                inventory_summary = gr.HTML()
                
                # Inventory Charts
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Valeur d'Inventaire par Catégorie")
                        inventory_value_chart = gr.Plot()
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Niveaux de Stock Actuels")
                        stock_level_chart = gr.Plot()
                    
                    with gr.Column():
                        gr.Markdown("### Articles en Stock Faible")
                        low_stock_chart = gr.Plot()
            
            # Sales Dashboard Tab
            with gr.TabItem("Tableau de Bord Ventes", elem_classes=["tab-button"]):
                # Date filter section (specific to Sales)
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Filtrer par Date")
                        with gr.Row():
                            # Date inputs
                            sales_start_date = gr.Textbox(
                                label="Date de début (AAAA-MM-JJ)",
                                placeholder="AAAA-MM-JJ",
                                value=(datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
                            )
                            
                            sales_end_date = gr.Textbox(
                                label="Date de fin (AAAA-MM-JJ)",
                                placeholder="AAAA-MM-JJ",
                                value=datetime.now().strftime("%Y-%m-%d")
                            )
                            
                            apply_sales_date_filter = gr.Button("Appliquer le Filtre", elem_classes=["filter-button"])
                
                # Sales Summary section
                gr.Markdown("### Résumé des Ventes")
                sales_summary = gr.HTML()
                
                # Sales Charts
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Ventes par Produit")
                        sales_by_product_chart = gr.Plot()
                    
                    with gr.Column():
                        gr.Markdown("### Ventes par Client")
                        sales_by_client_chart = gr.Plot()
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Ventes par Source")
                        sales_by_source_chart = gr.Plot()
                    
                    with gr.Column():
                        gr.Markdown("### Ventes par Ville")
                        sales_by_city_chart = gr.Plot()
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Statut des Commandes")
                        order_status_chart = gr.Plot()
                    
                    with gr.Column():
                        gr.Markdown("### Statut des Paiements")
                        payment_status_chart = gr.Plot()
            
            # Suppliers Dashboard Tab
            with gr.TabItem("Tableau de Bord Fournisseurs", elem_classes=["tab-button"]):
                # Date filter section (dedicated to Suppliers)
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Filtrer par Date")
                        with gr.Row():
                            # Date inputs for Suppliers
                            suppliers_start_date = gr.Textbox(
                                label="Date de début (AAAA-MM-JJ)",
                                placeholder="AAAA-MM-JJ",
                                value=(datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
                            )
                            
                            suppliers_end_date = gr.Textbox(
                                label="Date de fin (AAAA-MM-JJ)",
                                placeholder="AAAA-MM-JJ",
                                value=datetime.now().strftime("%Y-%m-%d")
                            )
                            
                            apply_suppliers_date_filter = gr.Button("Appliquer le Filtre", elem_classes=["filter-button"])
                
                # Suppliers Summary section
                gr.Markdown("### Résumé des Fournisseurs")
                supplier_summary = gr.HTML()
                
                # Suppliers Charts
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Top Fournisseurs par Montant")
                        suppliers_by_amount_chart = gr.Plot()
                    
                    with gr.Column():
                        gr.Markdown("### Statut des Paiements Fournisseurs")
                        supplier_payment_status_chart = gr.Plot()
            
            # AI Assistant Tab
            with gr.TabItem("Assistant IA", elem_classes=["tab-button"]):
                gr.Markdown("""
                ## 🤖 Assistant E-commerce
                
                Posez des questions sur vos données d'inventaire, de ventes et de fournisseurs en langage naturel.
                """)
                
                # Example questions section
                with gr.Accordion("Questions Exemples", open=True):
                    example_questions = [
                        "Quels produits sont en stock faible?",
                        "Quel est mon produit le plus vendu?",
                        "Quelle est la valeur totale de mon inventaire?",
                        "Combien de commandes sont en attente de livraison?",
                        "Qui sont mes meilleurs clients par montant d'achat?",
                        "Quelle est la répartition des ventes par source?",
                        "Quel fournisseur a le plus grand montant impayé?",
                        "Quel est mon produit le plus vendu?",
                        "Quelle est la valeur totale de mon inventaire?",
                        "Combien de commandes sont en attente de livraison?",
                        "Qui sont mes meilleurs clients par montant d'achat?",
                        "Quelle est la répartition des ventes par source?",
                        "Quel fournisseur a le plus grand montant impayé?",
                        "Combien de produits sont en rupture de stock?",
                        "Quel est le taux de conversion des commandes?",
                        "Quelles sont les tendances de vente par ville?"
                    ]
                    
                    example_buttons = []
                    for i in range(0, len(example_questions), 2):
                        with gr.Row():
                            for j in range(2):
                                if i + j < len(example_questions):
                                    example_buttons.append(gr.Button(example_questions[i + j], size="sm"))
                
                with gr.Row():
                    with gr.Column():
                        ai_input = gr.Textbox(
                            label="Votre question",
                            placeholder="Exemple: Quels produits sont en stock faible?",
                            lines=2
                        )
                        ai_button = gr.Button("Poser ma question", elem_classes=["primary-button"])
                
                ai_output = gr.Markdown(
                    label="Réponse",
                    value="Connectez-vous à votre Google Sheet et posez une question pour commencer."
                )
    
    # Set up the event handlers
    connect_button.click(
        fn=process_sheet,
        inputs=[sheet_url_input],
        outputs=[
            status_html,
            combined_data_json,
            dashboard_section,
            inventory_value_chart,
            stock_level_chart,
            low_stock_chart,
            inventory_summary,
            sales_by_product_chart,
            sales_by_client_chart,
            sales_by_source_chart,
            sales_by_city_chart,
            order_status_chart,
            payment_status_chart,
            sales_summary,
            suppliers_by_amount_chart,
            supplier_payment_status_chart,
            supplier_summary,
            sales_start_date,
            sales_end_date,
            suppliers_start_date,
            suppliers_end_date
        ]
    )
    
    # Set up sales date filter event handler
    apply_sales_date_filter.click(
        fn=update_sales_dashboard_with_date_filter,
        inputs=[combined_data_json, sales_start_date, sales_end_date],
        outputs=[
            sales_by_product_chart,
            sales_by_client_chart,
            sales_by_source_chart,
            sales_by_city_chart,
            order_status_chart,
            payment_status_chart,
            sales_summary
        ]
    )
    
    # Set up suppliers date filter event handler
    apply_suppliers_date_filter.click(
        fn=update_suppliers_dashboard_with_date_filter,
        inputs=[combined_data_json, suppliers_start_date, suppliers_end_date],
        outputs=[
            suppliers_by_amount_chart,
            supplier_payment_status_chart,
            supplier_summary
        ]
    )
    
    # Set up AI assistant event handler
    ai_button.click(
        fn=handle_user_query,
        inputs=[ai_input, combined_data_json],
        outputs=[ai_output]
    )
    
    # Add click handlers for example buttons
    for i, example_button in enumerate(example_buttons):
        example_button.click(
            fn=lambda example=example_questions[i]: example,
            inputs=[],
            outputs=[ai_input]
        ).then(
            fn=handle_user_query,
            inputs=[ai_input, combined_data_json],
            outputs=[ai_output]
        )

# Launch the app
if __name__ == "__main__":
    app.launch()