import requests
import json
import pandas as pd
import numpy as np

# Gemini API configuration
GEMINI_API_KEY = "AIzaSyDuDl8wzjgU2LaauLFq02TLSPOarn2yzAI"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

def prepare_inventory_context(df):
    """
    Prepare inventory (stock) data as context for Gemini.
    Returns a string representation of the data that can be included in the prompt.
    """
    if df is None or df.empty:
        return "No inventory data available."
    
    # Convert DataFrame to a more readable format for the AI
    data_context = "DONNÉES D'INVENTAIRE (STOCK):\n"
    
    # Print full raw data for debugging (first 10 rows)
    data_context += "Données brutes (10 premières lignes):\n"
    data_context += df.head(10).to_string() + "\n\n"
    
    # Add summary statistics
    total_products = len(df)
    total_quantity = df['Quantité disponible'].sum() if 'Quantité disponible' in df.columns else 0
    categories = df['Catégorie'].unique() if 'Catégorie' in df.columns else []
    
    data_context += f"- Total des produits uniques: {total_products}\n"
    data_context += f"- Total des articles en stock: {total_quantity}\n"
    data_context += f"- Catégories de produits: {', '.join([str(cat) for cat in categories])}\n"
    
    # Calculate low stock items
    if 'Quantité disponible' in df.columns and 'Nom du produit' in df.columns:
        low_stock = df[df['Quantité disponible'] < 5]
        low_stock_count = len(low_stock)
        data_context += f"- Produits en stock faible (moins de 5 unités): {low_stock_count}\n"
        
        # Show low stock items
        if not low_stock.empty:
            data_context += "\nProduits en stock faible:\n"
            for _, row in low_stock.iterrows():
                product_name = row.get('Nom du produit', 'Unknown')
                quantity = row.get('Quantité disponible', 0)
                data_context += f"- {product_name}: {quantity} unités disponibles\n"
    
    # Calculate inventory value
    if 'Quantité disponible' in df.columns and 'Prix' in df.columns:
        inventory_value = (df['Quantité disponible'] * df['Prix']).sum()
        data_context += f"\nValeur totale de l'inventaire: {inventory_value:.2f} DH\n"
        
        # Value by category
        if 'Catégorie' in df.columns:
            category_values = df.groupby('Catégorie').apply(lambda x: (x['Quantité disponible'] * x['Prix']).sum())
            data_context += "\nValeur de l'inventaire par catégorie:\n"
            for category, value in category_values.items():
                data_context += f"- {category}: {value:.2f} DH\n"
    
    return data_context

def prepare_orders_context(df):
    """
    Prepare orders data as context for Gemini.
    Returns a string representation of the data that can be included in the prompt.
    """
    if df is None or df.empty:
        return "No orders data available."
    
    # Convert DataFrame to a more readable format for the AI
    data_context = "DONNÉES DE COMMANDES:\n"
    
    # Print full raw data for debugging (first 10 rows)
    data_context += "Données brutes (10 premières lignes):\n"
    data_context += df.head(10).to_string() + "\n\n"
    
    # Add summary statistics
    total_orders = len(df)
    data_context += f"- Total des commandes: {total_orders}\n"
    
    # Calculate total revenue
    if 'montant total' in df.columns:
        df['montant total'] = pd.to_numeric(df['montant total'], errors='coerce')
        total_revenue = df['montant total'].sum()
        data_context += f"- Chiffre d'affaires total: {total_revenue:.2f} DH\n"
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        data_context += f"- Valeur moyenne des commandes: {avg_order_value:.2f} DH\n"
    
    # Count unique clients
    if 'Nom du client' in df.columns:
        unique_clients = df['Nom du client'].nunique()
        data_context += f"- Nombre de clients uniques: {unique_clients}\n"
        
        # Top clients
        client_sales = df.groupby('Nom du client')['montant total'].sum().sort_values(ascending=False)
        data_context += "\nTop clients par montant d'achat:\n"
        for client, amount in client_sales.head(5).items():
            data_context += f"- {client}: {amount:.2f} DH\n"
    
    # Count orders by source
    if 'Source' in df.columns:
        source_counts = df['Source'].value_counts()
        source_percentages = 100 * source_counts / len(df)
        data_context += "\nCommandes par source:\n"
        for source, count in source_counts.items():
            percentage = source_percentages[source]
            data_context += f"- {source}: {count} commandes ({percentage:.1f}%)\n"
    
    # Count orders by status
    if 'Statut de livraison' in df.columns:
        status_counts = df['Statut de livraison'].value_counts()
        data_context += "\nCommandes par statut de livraison:\n"
        for status, count in status_counts.items():
            data_context += f"- {status}: {count} commandes\n"
    
    # Count orders by payment status
    if 'Statut de paiement' in df.columns:
        payment_counts = df['Statut de paiement'].value_counts()
        data_context += "\nCommandes par statut de paiement:\n"
        for status, count in payment_counts.items():
            data_context += f"- {status}: {count} commandes\n"
    
    # Top products
    if 'Nom du Produit' in df.columns and 'montant total' in df.columns:
        product_sales = df.groupby('Nom du Produit')['montant total'].sum().sort_values(ascending=False)
        data_context += "\nProduits les plus vendus par montant:\n"
        for product, amount in product_sales.head(10).items():
            data_context += f"- {product}: {amount:.2f} DH\n"
    
    return data_context

def prepare_suppliers_context(df):
    """
    Prepare suppliers data as context for Gemini.
    Returns a string representation of the data that can be included in the prompt.
    """
    if df is None or df.empty:
        return "No suppliers data available."
    
    # Convert DataFrame to a more readable format for the AI
    data_context = "DONNÉES DES FOURNISSEURS:\n"
    
    # Print full raw data for debugging (first 10 rows)
    data_context += "Données brutes (10 premières lignes):\n"
    data_context += df.head(10).to_string() + "\n\n"
    
    # Add summary statistics
    total_suppliers = df['Nom du fournisseur'].nunique() if 'Nom du fournisseur' in df.columns else 0
    data_context += f"- Total des fournisseurs uniques: {total_suppliers}\n"
    
    # Calculate total purchase amount
    if 'Montant totale' in df.columns:
        df['Montant totale'] = pd.to_numeric(df['Montant totale'], errors='coerce')
        total_purchases = df['Montant totale'].sum()
        data_context += f"- Montant total des achats: {total_purchases:.2f} DH\n"
    
    # Calculate paid and outstanding amounts
    if 'Montant Payé' in df.columns and 'Reste' in df.columns:
        df['Montant Payé'] = pd.to_numeric(df['Montant Payé'], errors='coerce')
        df['Reste'] = pd.to_numeric(df['Reste'], errors='coerce')
        
        total_paid = df['Montant Payé'].sum()
        total_outstanding = df['Reste'].sum()
        
        data_context += f"- Montant total payé aux fournisseurs: {total_paid:.2f} DH\n"
        data_context += f"- Montant total impayé: {total_outstanding:.2f} DH\n"
        
        payment_rate = (total_paid / total_purchases * 100) if 'Montant totale' in df.columns and total_purchases > 0 else 0
        data_context += f"- Taux de paiement global: {payment_rate:.1f}%\n"
    
    # Top suppliers
    if 'Nom du fournisseur' in df.columns and 'Montant totale' in df.columns:
        supplier_purchases = df.groupby('Nom du fournisseur')['Montant totale'].sum().sort_values(ascending=False)
        data_context += "\nTop fournisseurs par montant d'achat:\n"
        for supplier, amount in supplier_purchases.head(5).items():
            data_context += f"- {supplier}: {amount:.2f} DH\n"
    
    # Suppliers with outstanding balances
    if 'Nom du fournisseur' in df.columns and 'Reste' in df.columns:
        supplier_outstanding = df.groupby('Nom du fournisseur')['Reste'].sum().sort_values(ascending=False)
        data_context += "\nFournisseurs avec montants impayés:\n"
        for supplier, amount in supplier_outstanding[supplier_outstanding > 0].head(10).items():
            data_context += f"- {supplier}: {amount:.2f} DH impayés\n"
    
    # Products by supplier
    if 'Nom du fournisseur' in df.columns and 'Nom du produit' in df.columns and 'Quantite' in df.columns:
        data_context += "\nProduits par fournisseur:\n"
        for supplier in df['Nom du fournisseur'].unique():
            supplier_products = df[df['Nom du fournisseur'] == supplier]['Nom du produit'].unique()
            data_context += f"- {supplier}: {', '.join(supplier_products)}\n"
    
    return data_context

def query_gemini_ai(prompt, data_context):
    """
    Query Gemini AI with the given prompt and inventory/sales data context.
    
    Args:
        prompt: The user's question
        data_context: String representation of inventory/sales data
    
    Returns:
        Gemini's response as a string
    """
    # Construct the full prompt with data context and clear instructions
    full_prompt = """Tu es un assistant d'analyse de données pour une entreprise de commerce électronique. 
Tu as accès aux données d'inventaire, de commandes et de fournisseurs. Voici les données :

{}

Basé sur ces données, réponds à la question suivante :
{}

Sois précis et concis, et mentionne des chiffres spécifiques des données quand c'est pertinent.
Utilise uniquement les informations disponibles dans les données fournies, ne fais pas de suppositions.
Réponds toujours en français.
""".format(data_context, prompt)
    
    # Prepare the request payload
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": full_prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 1024
        }
    }
    
    # Set headers for the API request
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        # Make the API request to Gemini
        response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(payload))
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response
            response_data = response.json()
            
            # Extract the generated text
            if "candidates" in response_data and len(response_data["candidates"]) > 0:
                if "content" in response_data["candidates"][0]:
                    content = response_data["candidates"][0]["content"]
                    if "parts" in content and len(content["parts"]) > 0:
                        return content["parts"][0]["text"]
            
            return "Désolé, je n'ai pas pu générer une réponse basée sur les données."
        else:
            # Handle API error
            error_message = f"Erreur API: {response.status_code}"
            try:
                error_data = response.json()
                if "error" in error_data and "message" in error_data["error"]:
                    error_message += f" - {error_data['error']['message']}"
            except:
                pass
            
            return f"Désolé, il y a eu une erreur de connexion à l'assistant IA: {error_message}"
    
    except Exception as e:
        # Handle any other exceptions
        return f"Désolé, il y a eu une erreur: {str(e)}"

def handle_user_query(query, combined_data_json=None):
    """
    Handle a user query for the AI assistant.
    
    Args:
        query: User's question as a string
        combined_data_json: JSON string representation of multiple DataFrames
    
    Returns:
        AI response
    """
    # If no data is loaded, inform the user
    if combined_data_json is None:
        return "Veuillez d'abord vous connecter à un Google Sheet pour utiliser l'assistant IA."
    
    try:
        # Convert JSON back to dictionary of DataFrames
        combined_data = pd.read_json(combined_data_json, typ='series').to_dict()
        
        # Initialize data context
        full_data_context = ""
        
        # Process stock data
        if "stock" in combined_data and combined_data["stock"]:
            stock_df = pd.read_json(combined_data["stock"], orient='split')
            inventory_context = prepare_inventory_context(stock_df)
            full_data_context += inventory_context + "\n\n"
        
        # Process orders data
        if "commandes" in combined_data and combined_data["commandes"]:
            commandes_df = pd.read_json(combined_data["commandes"], orient='split')
            orders_context = prepare_orders_context(commandes_df)
            full_data_context += orders_context + "\n\n"
        
        # Process suppliers data
        if "fournisseur" in combined_data and combined_data["fournisseur"]:
            fournisseur_df = pd.read_json(combined_data["fournisseur"], orient='split')
            suppliers_context = prepare_suppliers_context(fournisseur_df)
            full_data_context += suppliers_context
        
        # Query the AI with the user's question and the data context
        response = query_gemini_ai(query, full_data_context)
        
        return response
    
    except Exception as e:
        return f"Erreur lors du traitement de votre requête: {str(e)}"