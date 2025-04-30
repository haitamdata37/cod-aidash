import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
import numpy as np

# Define consistent color scheme
GOOD_COLOR = "#4CAF50"  # Green for positive/revenue values
BAD_COLOR = "#F44336"   # Red for negative/expense values
TAX_COLOR = "#FFC107"   # Yellow for tax-related values/warnings
NEUTRAL_COLOR = "#3F51B5"  # Blue for neutral values

def create_inventory_value_chart(df):
    """Create inventory value chart by category with improved distinct colors."""
    if df is None or df.empty:
        # Create an empty chart with a message if no data
        fig = go.Figure()
        fig.add_annotation(
            text="Aucune donnée disponible pour ce graphique",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=20, color="#777777")
        )
        fig.update_layout(
            title={
                'text': "Valeur d'inventaire par catégorie",
                'font': {'size': 22, 'color': '#333'}
            },
            height=450
        )
        return fig
    
    # Print dataframe columns to debug
    print("Columns in dataframe:", df.columns.tolist())
    
    # Check if required columns are present
    if 'Catégorie' not in df.columns:
        # If category column doesn't exist, try to find a similar one
        category_cols = [col for col in df.columns if 'categ' in col.lower()]
        if category_cols:
            df['Catégorie'] = df[category_cols[0]]
        else:
            # Create a default category if none exists
            df['Catégorie'] = 'Non catégorisé'
    
    # Ensure we have a price column for value calculation
    if 'Prix' not in df.columns:
        # Check for similar price columns
        price_cols = [col for col in df.columns if 'prix' in col.lower()]
        if price_cols:
            df['Prix'] = pd.to_numeric(df[price_cols[0]], errors='coerce').fillna(0)
        else:
            # Use a default price if none exists
            df['Prix'] = 1.0
    
    # Calculate value by category
    try:
        # Make sure quantity column is numeric
        if 'Quantité disponible' in df.columns:
            df['Quantité disponible'] = pd.to_numeric(df['Quantité disponible'], errors='coerce').fillna(0)
            df['Valeur'] = df['Quantité disponible'] * df['Prix']
        else:
            # If quantity column doesn't exist, use a count of products
            df['Valeur'] = df['Prix']
            
        # Group by category
        category_values = df.groupby('Catégorie')['Valeur'].sum().reset_index()
        
        # If we ended up with empty results, create a default category
        if category_values.empty:
            category_values = pd.DataFrame({
                'Catégorie': ['Non catégorisé'],
                'Valeur': [df['Valeur'].sum()]
            })
        
        # Define a set of distinct, bold colors for better visibility
        distinct_colors = [
            '#4CAF50',  # Green
            '#2196F3',  # Blue
            '#F44336',  # Red
            '#FFC107',  # Amber
            '#9C27B0',  # Purple
            '#FF9800',  # Orange
            '#00BCD4',  # Cyan
            '#795548',  # Brown
            '#607D8B',  # Blue Grey
            '#E91E63',  # Pink
            '#3F51B5',  # Indigo
            '#009688',  # Teal
            '#CDDC39',  # Lime
            '#FF5722'   # Deep Orange
        ]
        
        # Create the pie chart with distinct colors
        fig = go.Figure(data=[go.Pie(
            labels=category_values['Catégorie'],
            values=category_values['Valeur'],
            hole=0.4,  # Make it a donut chart for better visibility
            marker=dict(
                colors=distinct_colors[:len(category_values)],
                line=dict(color='#FFFFFF', width=2)
            ),
            textinfo='percent+label',
            textposition='inside',
            insidetextfont=dict(color='white'),
        )])
        
        fig.update_layout(
            title={
                'text': "Valeur d'inventaire par catégorie",
                'font': {'size': 22, 'color': '#333'}
            },
            margin=dict(l=40, r=40, t=60, b=40),
            height=450,
            plot_bgcolor='rgba(245, 245, 245, 0.8)',
            paper_bgcolor='white',
            font=dict(
                family="Arial, sans-serif",
                size=12,
                color="#333333"
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.1,
                xanchor="center",
                x=0.5
            )
        )
        
        return fig
    except Exception as e:
        # If any error occurs, print it and return a fallback chart
        print(f"Error creating inventory value chart: {str(e)}")
        
        # Create a fallback chart
        fig = go.Figure()
        fig.add_annotation(
            text=f"Erreur lors de la création du graphique: {str(e)}",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            showarrow=False,
            font=dict(size=16, color="#C62828")
        )
        fig.update_layout(
            title={
                'text': "Valeur d'inventaire par catégorie",
                'font': {'size': 22, 'color': '#333'}
            },
            height=450
        )
        return fig

def create_stock_level_chart(df):
    """Create stock level chart for products."""
    if df is None or df.empty:
        return None
        
    if 'Nom du produit' in df.columns and 'Quantité disponible' in df.columns:
        # Sort by available quantity
        plot_df = df.sort_values('Quantité disponible', ascending=False).head(15)
        
        # Create a color gradient based on stock levels - red for low stock, green for good stock
        colors = [BAD_COLOR if x < 5 else GOOD_COLOR for x in plot_df['Quantité disponible']]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=plot_df['Nom du produit'],
            y=plot_df['Quantité disponible'],
            marker_color=colors,
            name='Quantité disponible'
        ))
        
        fig.update_layout(
            title={
                'text': 'Niveaux de stock actuels',
                'font': {'size': 22, 'color': '#333'}
            },
            xaxis_title='Produit',
            yaxis_title='Quantité disponible',
            hovermode='closest',
            margin=dict(l=40, r=40, t=60, b=40),
            height=450,
            plot_bgcolor='rgba(245, 245, 245, 0.8)',
            paper_bgcolor='white',
            font=dict(
                family="Arial, sans-serif",
                size=12,
                color="#333333"
            )
        )
        
        # Rotate x-axis labels for better readability
        fig.update_xaxes(tickangle=45)
        
        # Add grid lines
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(230, 230, 230, 0.8)'
        )
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(230, 230, 230, 0.8)'
        )
        
        return fig
    
    return None

def create_low_stock_chart(df):
    """Create chart highlighting low stock items."""
    if df is None or df.empty:
        return None
        
    if 'Nom du produit' in df.columns and 'Quantité disponible' in df.columns:
        # Filter to low stock items (less than 5 units)
        low_stock_df = df[df['Quantité disponible'] < 5].copy()
        low_stock_df = low_stock_df.sort_values('Quantité disponible')
        
        # If nothing is low on stock
        if low_stock_df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="Aucun produit en stock faible!",
                x=0.5, y=0.5,
                xref="paper", yref="paper",
                showarrow=False,
                font=dict(size=20, color=GOOD_COLOR)  # Green for good
            )
            fig.update_layout(
                title={
                    'text': 'Produits en stock faible (moins de 5 unités)',
                    'font': {'size': 22, 'color': '#333'}
                },
                height=450
            )
            return fig
            
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=low_stock_df['Nom du produit'],
            y=low_stock_df['Quantité disponible'],
            marker_color=TAX_COLOR,  # Yellow for warning
            name='Quantité disponible'
        ))
        
        fig.update_layout(
            title={
                'text': 'Produits en stock faible (moins de 5 unités)',
                'font': {'size': 22, 'color': '#333'}
            },
            xaxis_title='Produit',
            yaxis_title='Quantité disponible',
            hovermode='closest',
            margin=dict(l=40, r=40, t=60, b=40),
            height=450,
            plot_bgcolor='rgba(245, 245, 245, 0.8)',
            paper_bgcolor='white',
            font=dict(
                family="Arial, sans-serif",
                size=12,
                color="#333333"
            )
        )
        
        # Add grid lines
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(230, 230, 230, 0.8)'
        )
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(230, 230, 230, 0.8)'
        )
        
        return fig
    
    return None

def create_sales_by_product_chart(df):
    """Create chart showing sales by product."""
    if df is None or df.empty:
        return None
        
    if 'Nom du Produit' in df.columns and 'montant total' in df.columns:
        try:
            # Ensure numeric values
            df['montant total'] = pd.to_numeric(df['montant total'], errors='coerce')
            
            # Group by product and sum the total amount
            product_sales = df.groupby('Nom du Produit')['montant total'].sum().reset_index()
            
            # Sort and take top 10
            product_sales = product_sales.sort_values('montant total', ascending=False).head(10)
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=product_sales['Nom du Produit'],
                y=product_sales['montant total'],
                marker_color=GOOD_COLOR,  # Green for revenue/sales
                name='Ventes totales'
            ))
            
            fig.update_layout(
                title={
                    'text': 'Top 10 des ventes par produit',
                    'font': {'size': 22, 'color': '#333'}
                },
                xaxis_title='Produit',
                yaxis_title='Montant total (DH)',
                hovermode='closest',
                margin=dict(l=40, r=40, t=60, b=40),
                height=450,
                plot_bgcolor='rgba(245, 245, 245, 0.8)',
                paper_bgcolor='white',
                font=dict(
                    family="Arial, sans-serif",
                    size=12,
                    color="#333333"
                )
            )
            
            # Rotate x-axis labels for better readability
            fig.update_xaxes(tickangle=45)
            
            # Add grid lines
            fig.update_xaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(230, 230, 230, 0.8)'
            )
            fig.update_yaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(230, 230, 230, 0.8)'
            )
            
            # Format y-axis as currency
            fig.update_yaxes(
                tickprefix='DH ',
                separatethousands=True
            )
            
            return fig
        except Exception as e:
            print(f"Error creating sales by product chart: {str(e)}")
    
    return None

def create_sales_by_client_chart(df):
    """Create chart showing sales by client."""
    if df is None or df.empty:
        return None
        
    if 'Nom du client' in df.columns and 'montant total' in df.columns:
        try:
            # Ensure numeric values
            df['montant total'] = pd.to_numeric(df['montant total'], errors='coerce')
            
            # Group by client and sum the total amount
            client_sales = df.groupby('Nom du client')['montant total'].sum().reset_index()
            
            # Sort and take top 10
            client_sales = client_sales.sort_values('montant total', ascending=False).head(10)
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=client_sales['Nom du client'],
                y=client_sales['montant total'],
                marker_color=GOOD_COLOR,  # Green for revenue/sales
                name='Ventes totales'
            ))
            
            fig.update_layout(
                title={
                    'text': 'Top 10 des ventes par client',
                    'font': {'size': 22, 'color': '#333'}
                },
                xaxis_title='Client',
                yaxis_title='Montant total (DH)',
                hovermode='closest',
                margin=dict(l=40, r=40, t=60, b=40),
                height=450,
                plot_bgcolor='rgba(245, 245, 245, 0.8)',
                paper_bgcolor='white',
                font=dict(
                    family="Arial, sans-serif",
                    size=12,
                    color="#333333"
                )
            )
            
            # Add grid lines
            fig.update_xaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(230, 230, 230, 0.8)'
            )
            fig.update_yaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(230, 230, 230, 0.8)'
            )
            
            # Format y-axis as currency
            fig.update_yaxes(
                tickprefix='DH ',
                separatethousands=True
            )
            
            return fig
        except Exception as e:
            print(f"Error creating sales by client chart: {str(e)}")
    
    return None

def create_sales_by_source_chart(df):
    """Create chart showing sales by source with improved distinct colors."""
    if df is None or df.empty:
        return None
        
    if 'Source' in df.columns and 'montant total' in df.columns:
        try:
            # Ensure numeric values
            df['montant total'] = pd.to_numeric(df['montant total'], errors='coerce')
            
            # Group by source and sum the total amount
            source_sales = df.groupby('Source')['montant total'].sum().reset_index()
            
            # Define a set of distinct, bold colors for better visibility
            distinct_colors = [
                '#4CAF50',  # Green
                '#2196F3',  # Blue
                '#F44336',  # Red
                '#FFC107',  # Amber
                '#9C27B0',  # Purple
                '#FF9800',  # Orange
                '#00BCD4',  # Cyan
                '#795548',  # Brown
                '#607D8B',  # Blue Grey
                '#E91E63',  # Pink
                '#3F51B5',  # Indigo
                '#009688',  # Teal
                '#CDDC39',  # Lime
                '#FF5722'   # Deep Orange
            ]
            
            # Create the pie chart with distinct colors
            fig = go.Figure(data=[go.Pie(
                labels=source_sales['Source'],
                values=source_sales['montant total'],
                hole=0.4,  # Make it a donut chart for better visibility
                marker=dict(
                    colors=distinct_colors[:len(source_sales)],
                    line=dict(color='#FFFFFF', width=2)
                ),
                textinfo='percent+label',
                textposition='inside',
                insidetextfont=dict(color='white'),
            )])
            
            fig.update_layout(
                title={
                    'text': 'Ventes par source',
                    'font': {'size': 22, 'color': '#333'}
                },
                margin=dict(l=40, r=40, t=60, b=40),
                height=450,
                plot_bgcolor='rgba(245, 245, 245, 0.8)',
                paper_bgcolor='white',
                font=dict(
                    family="Arial, sans-serif",
                    size=12,
                    color="#333333"
                ),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.1,
                    xanchor="center",
                    x=0.5
                )
            )
            
            return fig
        except Exception as e:
            print(f"Error creating sales by source chart: {str(e)}")
    
    return None

def create_order_status_chart(df):
    """Create chart showing order status distribution."""
    if df is None or df.empty:
        return None
        
    if 'Statut de livraison' in df.columns:
        try:
            # Count orders by delivery status
            status_counts = df['Statut de livraison'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            
            # Custom color mapping for status
            color_map = {
                'Livré': GOOD_COLOR,    # Green for delivered
                'En attente': TAX_COLOR, # Yellow for pending
                'Retour': BAD_COLOR     # Red for returns
            }
            
            # Map known colors and provide default for unknown status
            colors = [color_map.get(status, '#9E9E9E') for status in status_counts['Status']]
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=status_counts['Status'],
                y=status_counts['Count'],
                marker_color=colors,
                name='Nombre de commandes'
            ))
            
            fig.update_layout(
                title={
                    'text': 'Statut des commandes',
                    'font': {'size': 22, 'color': '#333'}
                },
                xaxis_title='Statut',
                yaxis_title='Nombre de commandes',
                hovermode='closest',
                margin=dict(l=40, r=40, t=60, b=40),
                height=450,
                plot_bgcolor='rgba(245, 245, 245, 0.8)',
                paper_bgcolor='white',
                font=dict(
                    family="Arial, sans-serif",
                    size=12,
                    color="#333333"
                )
            )
            
            # Add grid lines
            fig.update_xaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(230, 230, 230, 0.8)'
            )
            fig.update_yaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(230, 230, 230, 0.8)'
            )
            
            return fig
        except Exception as e:
            print(f"Error creating order status chart: {str(e)}")
    
    return None

def create_payment_status_chart(df):
    """Create chart showing payment status distribution."""
    if df is None or df.empty:
        return None
        
    if 'Statut de paiement' in df.columns:
        try:
            # Count orders by payment status
            status_counts = df['Statut de paiement'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            
            # Custom color mapping for status
            color_map = {
                'Payé': GOOD_COLOR,      # Green for paid
                'En attente': TAX_COLOR,  # Yellow for pending
                'Non Payé': BAD_COLOR     # Red for unpaid
            }
            
            # Map known colors and provide default for unknown status
            colors = [color_map.get(status, '#9E9E9E') for status in status_counts['Status']]
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=status_counts['Status'],
                y=status_counts['Count'],
                marker_color=colors,
                name='Nombre de commandes'
            ))
            
            fig.update_layout(
                title={
                    'text': 'Statut des paiements',
                    'font': {'size': 22, 'color': '#333'}
                },
                xaxis_title='Statut',
                yaxis_title='Nombre de commandes',
                hovermode='closest',
                margin=dict(l=40, r=40, t=60, b=40),
                height=450,
                plot_bgcolor='rgba(245, 245, 245, 0.8)',
                paper_bgcolor='white',
                font=dict(
                    family="Arial, sans-serif",
                    size=12,
                    color="#333333"
                )
            )
            
            # Add grid lines
            fig.update_xaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(230, 230, 230, 0.8)'
            )
            fig.update_yaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(230, 230, 230, 0.8)'
            )
            
            return fig
        except Exception as e:
            print(f"Error creating payment status chart: {str(e)}")
    
    return None

def create_suppliers_by_amount_chart(df):
    """Create chart showing spending by supplier."""
    if df is None or df.empty:
        return None
        
    if 'Nom du fournisseur' in df.columns and 'Montant totale' in df.columns:
        try:
            # Ensure numeric values
            df['Montant totale'] = pd.to_numeric(df['Montant totale'], errors='coerce')
            
            # Group by supplier and sum the total amount
            supplier_spending = df.groupby('Nom du fournisseur')['Montant totale'].sum().reset_index()
            
            # Sort and take top 10
            supplier_spending = supplier_spending.sort_values('Montant totale', ascending=False).head(10)
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=supplier_spending['Nom du fournisseur'],
                y=supplier_spending['Montant totale'],
                marker_color=BAD_COLOR,  # Red for expenses
                name='Montant total'
            ))
            
            fig.update_layout(
                title={
                    'text': 'Top 10 des fournisseurs par montant',
                    'font': {'size': 22, 'color': '#333'}
                },
                xaxis_title='Fournisseur',
                yaxis_title='Montant total (DH)',
                hovermode='closest',
                margin=dict(l=40, r=40, t=60, b=40),
                height=450,
                plot_bgcolor='rgba(245, 245, 245, 0.8)',
                paper_bgcolor='white',
                font=dict(
                    family="Arial, sans-serif",
                    size=12,
                    color="#333333"
                )
            )
            
            # Rotate x-axis labels for better readability
            fig.update_xaxes(tickangle=45)
            
            # Add grid lines
            fig.update_xaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(230, 230, 230, 0.8)'
            )
            fig.update_yaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(230, 230, 230, 0.8)'
            )
            
            # Format y-axis as currency
            fig.update_yaxes(
                tickprefix='DH ',
                separatethousands=True
            )
            
            return fig
        except Exception as e:
            print(f"Error creating suppliers by amount chart: {str(e)}")
    
    return None

def create_supplier_payment_status_chart(df):
    """Create chart showing supplier payment status."""
    if df is None or df.empty:
        return None
        
    if 'Nom du fournisseur' in df.columns and 'Montant totale' in df.columns and 'Montant Payé' in df.columns and 'Reste' in df.columns:
        try:
            # Ensure numeric values
            for col in ['Montant totale', 'Montant Payé', 'Reste']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Group by supplier
            supplier_payments = df.groupby('Nom du fournisseur').agg({
                'Montant totale': 'sum',
                'Montant Payé': 'sum',
                'Reste': 'sum'
            }).reset_index()
            
            # Sort by total amount
            supplier_payments = supplier_payments.sort_values('Montant totale', ascending=False).head(10)
            
            fig = go.Figure()
            
            # Add paid amount bars - GREEN for paid amounts (good)
            fig.add_trace(go.Bar(
                x=supplier_payments['Nom du fournisseur'],
                y=supplier_payments['Montant Payé'],
                name='Payé',
                marker_color=GOOD_COLOR
            ))
            
            # Add remaining amount bars - RED for remaining (bad)
            fig.add_trace(go.Bar(
                x=supplier_payments['Nom du fournisseur'],
                y=supplier_payments['Reste'],
                name='Reste à payer',
                marker_color=BAD_COLOR
            ))
            
            fig.update_layout(
                title={
                    'text': 'Statut des paiements par fournisseur',
                    'font': {'size': 22, 'color': '#333'}
                },
                xaxis_title='Fournisseur',
                yaxis_title='Montant (DH)',
                hovermode='closest',
                barmode='stack',
                margin=dict(l=40, r=40, t=60, b=40),
                height=450,
                plot_bgcolor='rgba(245, 245, 245, 0.8)',
                paper_bgcolor='white',
                font=dict(
                    family="Arial, sans-serif",
                    size=12,
                    color="#333333"
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            # Rotate x-axis labels for better readability
            fig.update_xaxes(tickangle=45)
            
            # Add grid lines
            fig.update_xaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(230, 230, 230, 0.8)'
            )
            fig.update_yaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(230, 230, 230, 0.8)'
            )
            
            # Format y-axis as currency
            fig.update_yaxes(
                tickprefix='DH ',
                separatethousands=True
            )
            
            return fig
        except Exception as e:
            print(f"Error creating supplier payment status chart: {str(e)}")
    
    return None

def create_sales_by_city_chart(df):
    """Create chart showing sales by city."""
    if df is None or df.empty:
        return None
        
    if 'Ville  client' in df.columns and 'montant total' in df.columns:
        try:
            # Ensure numeric values
            df['montant total'] = pd.to_numeric(df['montant total'], errors='coerce')
            
            # Group by city and sum the total amount
            city_sales = df.groupby('Ville  client')['montant total'].sum().reset_index()
            
            # Sort and take top 10
            city_sales = city_sales.sort_values('montant total', ascending=False).head(10)
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=city_sales['Ville  client'],
                y=city_sales['montant total'],
                marker_color=GOOD_COLOR,  # Green for revenue/sales
                name='Ventes totales'
            ))
            
            fig.update_layout(
                title={
                    'text': 'Top 10 des ventes par ville',
                    'font': {'size': 22, 'color': '#333'}
                },
                xaxis_title='Ville',
                yaxis_title='Montant total (DH)',
                hovermode='closest',
                margin=dict(l=40, r=40, t=60, b=40),
                height=450,
                plot_bgcolor='rgba(245, 245, 245, 0.8)',
                paper_bgcolor='white',
                font=dict(
                    family="Arial, sans-serif",
                    size=12,
                    color="#333333"
                )
            )
            
            # Rotate x-axis labels for better readability
            fig.update_xaxes(tickangle=45)
            
            # Add grid lines
            fig.update_xaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(230, 230, 230, 0.8)'
            )
            fig.update_yaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(230, 230, 230, 0.8)'
            )
            
            # Format y-axis as currency
            fig.update_yaxes(
                tickprefix='DH ',
                separatethousands=True
            )
            
            return fig
        except Exception as e:
            print(f"Error creating sales by city chart: {str(e)}")
    
    return None
    
def generate_inventory_summary(stock_df):
    """Generate inventory summary HTML."""
    if stock_df is None or stock_df.empty:
        return ""
    
    # Calculate total items in stock
    total_items = stock_df['Quantité disponible'].sum() if 'Quantité disponible' in stock_df.columns else 0
    
    # Calculate count of products
    product_count = len(stock_df) if 'Nom du produit' in stock_df.columns else 0
    
    # Calculate count of categories
    category_count = stock_df['Catégorie'].nunique() if 'Catégorie' in stock_df.columns else 0
    
    # Calculate low stock items (less than 5 units)
    low_stock_count = sum(stock_df['Quantité disponible'] < 5) if 'Quantité disponible' in stock_df.columns else 0
    
    # Calculate out of stock items
    out_of_stock_count = sum(stock_df['Quantité disponible'] <= 0) if 'Quantité disponible' in stock_df.columns else 0
    
    # Calculate inventory value if price is available
    inventory_value = 0
    if 'Quantité disponible' in stock_df.columns and 'Prix' in stock_df.columns:
        inventory_value = (stock_df['Quantité disponible'] * stock_df['Prix']).sum()
    
    # Generate HTML summary
    html = """
    <style>
    .summary-container {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    .summary-card {
        flex: 1;
        min-width: 200px;
        background: #1e1e2f; /* dark background */
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease;
    }
    .summary-card:hover {
        transform: translateY(-5px);
    }
    .card-title {
        margin: 0;
        font-size: 14px;
        color: #cccccc !important; /* lighter gray */
        font-weight: 600;
    }
    .card-value {
        margin: 10px 0 0;
        font-size: 24px;
        font-weight: 700;
    }
    .total-items { color: #3F51B5 !important; }   /* blue for neutral */
    .products { color: #4CAF50 !important; }      /* green for positive */
    .categories { color: #3F51B5 !important; }    /* blue for neutral */
    .low-stock { color: #FFC107 !important; }     /* yellow for warning */
    .out-of-stock { color: #F44336 !important; }  /* red for negative */
    .inventory-value { color: #4CAF50 !important; } /* green for positive (value) */
    </style>
    
    <div class="summary-container">
        <div class="summary-card">
            <h3 class="card-title">Total Articles</h3>
            <p class="card-value total-items">"""

    # Use simple string concatenation for numbers
    html += str(int(total_items))
    
    html += """</p>
        </div>
        
        <div class="summary-card">
            <h3 class="card-title">Produits Uniques</h3>
            <p class="card-value products">"""
    
    html += str(product_count)
    
    html += """</p>
        </div>
        
        <div class="summary-card">
            <h3 class="card-title">Catégories</h3>
            <p class="card-value categories">"""
    
    html += str(category_count)
    
    html += """</p>
        </div>
    </div>

    <div class="summary-container">
        <div class="summary-card">
            <h3 class="card-title">Stock Faible</h3>
            <p class="card-value low-stock">"""
    
    html += str(low_stock_count)
    
    html += """</p>
        </div>
        
        <div class="summary-card">
            <h3 class="card-title">Rupture de Stock</h3>
            <p class="card-value out-of-stock">"""
    
    html += str(out_of_stock_count)
    
    html += """</p>
        </div>
        
        <div class="summary-card">
            <h3 class="card-title">Valeur Inventaire</h3>
            <p class="card-value inventory-value">"""
    
    html += "{:,.2f}".format(inventory_value) + " DH"
    
    html += """</p>
        </div>
    </div>
    """
    
    return html

def generate_sales_summary(orders_df):
    """Generate sales summary HTML."""
    if orders_df is None or orders_df.empty:
        return ""
    
    # Calculate total sales amount
    total_sales = orders_df['montant total'].sum() if 'montant total' in orders_df.columns else 0
    
    # Calculate count of orders
    order_count = len(orders_df)
    
    # Calculate count of unique clients
    client_count = orders_df['Nom du client'].nunique() if 'Nom du client' in orders_df.columns else 0
    
    # Calculate average order value
    avg_order_value = total_sales / order_count if order_count > 0 else 0
    
    # Count delivered orders
    delivered_count = sum(orders_df['Statut de livraison'] == 'Livré') if 'Statut de livraison' in orders_df.columns else 0
    
    # Count paid orders
    paid_count = sum(orders_df['Statut de paiement'] == 'Payé') if 'Statut de paiement' in orders_df.columns else 0
    
    # Calculate rates
    delivery_rate = (delivered_count / order_count * 100) if order_count > 0 else 0
    payment_rate = (paid_count / order_count * 100) if order_count > 0 else 0
    
    # Generate HTML summary
    html = """
    <style>
    .summary-container {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    .summary-card {
        flex: 1;
        min-width: 200px;
        background: #1e1e2f; /* dark background */
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease;
    }
    .summary-card:hover {
        transform: translateY(-5px);
    }
    .card-title {
        margin: 0;
        font-size: 14px;
        color: #cccccc !important; /* lighter gray */
        font-weight: 600;
    }
    .card-value {
        margin: 10px 0 0;
        font-size: 24px;
        font-weight: 700;
    }
    .total-sales { color: #4CAF50 !important; }    /* green for revenue/positive */
    .orders { color: #3F51B5 !important; }         /* blue for neutral */
    .clients { color: #3F51B5 !important; }        /* blue for neutral */
    .avg-order { color: #4CAF50 !important; }      /* green for revenue/positive */
    .delivery-rate { color: #4CAF50 !important; }  /* green for good/positive */
    .payment-rate { color: #4CAF50 !important; }   /* green for good/positive */
    </style>
    
    <div class="summary-container">
        <div class="summary-card">
            <h3 class="card-title">Ventes Totales</h3>
            <p class="card-value total-sales">"""
    
    html += "{:,.2f}".format(total_sales) + " DH"
    
    html += """</p>
        </div>
        
        <div class="summary-card">
            <h3 class="card-title">Nombre de Commandes</h3>
            <p class="card-value orders">"""
    
    html += str(order_count)
    
    html += """</p>
        </div>
        
        <div class="summary-card">
            <h3 class="card-title">Clients Uniques</h3>
            <p class="card-value clients">"""
    
    html += str(client_count)
    
    html += """</p>
        </div>
    </div>

    <div class="summary-container">
        <div class="summary-card">
            <h3 class="card-title">Valeur Moyenne Commande</h3>
            <p class="card-value avg-order">"""
    
    html += "{:,.2f}".format(avg_order_value) + " DH"
    
    html += """</p>
        </div>
        
        <div class="summary-card">
            <h3 class="card-title">Taux de Livraison</h3>
            <p class="card-value delivery-rate">"""
    
    # Color-code based on value
    delivery_rate_color = "#4CAF50" if delivery_rate >= 80 else "#FFC107" if delivery_rate >= 50 else "#F44336"
    
    html += "<span style='color: " + delivery_rate_color + " !important;'>" + "{:.1f}".format(delivery_rate) + "%</span>"
    
    html += """</p>
        </div>
        
        <div class="summary-card">
            <h3 class="card-title">Taux de Paiement</h3>
            <p class="card-value payment-rate">"""
    
    # Color-code based on value
    payment_rate_color = "#4CAF50" if payment_rate >= 80 else "#FFC107" if payment_rate >= 50 else "#F44336"
    
    html += "<span style='color: " + payment_rate_color + " !important;'>" + "{:.1f}".format(payment_rate) + "%</span>"
    
    html += """</p>
        </div>
    </div>
    """
    
    return html

def generate_supplier_summary(supplier_df):
    """Generate supplier summary HTML."""
    if supplier_df is None or supplier_df.empty:
        return ""
    
    # Calculate total purchase amount
    total_purchases = supplier_df['Montant totale'].sum() if 'Montant totale' in supplier_df.columns else 0
    
    # Calculate count of unique suppliers
    supplier_count = supplier_df['Nom du fournisseur'].nunique() if 'Nom du fournisseur' in supplier_df.columns else 0
    
    # Calculate total paid amount
    total_paid = supplier_df['Montant Payé'].sum() if 'Montant Payé' in supplier_df.columns else 0
    
    # Calculate total remaining amount
    total_remaining = supplier_df['Reste'].sum() if 'Reste' in supplier_df.columns else 0
    
    # Calculate payment rate
    payment_rate = (total_paid / total_purchases * 100) if total_purchases > 0 else 0
    
    # Generate HTML summary with improved design
    html = """
    <style>
    .summary-container {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    .summary-card {
        flex: 1;
        min-width: 200px;
        background: #1e1e2f; /* dark background */
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease;
    }
    .summary-card:hover {
        transform: translateY(-5px);
    }
    .card-title {
        margin: 0;
        font-size: 14px;
        color: #cccccc !important; /* lighter gray */
        font-weight: 600;
    }
    .card-value {
        margin: 10px 0 0;
        font-size: 24px;
        font-weight: 700;
    }
    .total-purchases { color: #F44336 !important; } /* red for expenses/negative */
    .suppliers { color: #3F51B5 !important; }      /* blue for neutral */
    .total-paid { color: #4CAF50 !important; }     /* green for positive */
    .total-remaining { color: #F44336 !important; } /* red for negative */
    .payment-rate { color: #4CAF50 !important; }   /* green for positive */
    </style>
    
    <div class="summary-container">
        <div class="summary-card">
            <h3 class="card-title">Achats Totaux</h3>
            <p class="card-value total-purchases">"""
    
    html += "{:,.2f}".format(total_purchases) + " DH"
    
    html += """</p>
        </div>
        
        <div class="summary-card">
            <h3 class="card-title">Fournisseurs</h3>
            <p class="card-value suppliers">"""
    
    html += str(supplier_count)
    
    html += """</p>
        </div>
    </div>

    <div class="summary-container">
        <div class="summary-card">
            <h3 class="card-title">Montant Payé</h3>
            <p class="card-value total-paid">"""
    
    html += "{:,.2f}".format(total_paid) + " DH"
    
    html += """</p>
        </div>
        
        <div class="summary-card">
            <h3 class="card-title">Reste à Payer</h3>
            <p class="card-value total-remaining">"""
    
    html += "{:,.2f}".format(total_remaining) + " DH"
    
    html += """</p>
        </div>
        
        <div class="summary-card">
            <h3 class="card-title">Taux de Paiement</h3>
            <p class="card-value payment-rate">"""
    
    # Color-code based on value
    payment_rate_color = "#4CAF50" if payment_rate >= 80 else "#FFC107" if payment_rate >= 50 else "#F44336"
    
    html += "<span style='color: " + payment_rate_color + " !important;'>" + "{:.1f}".format(payment_rate) + "%</span>"
    
    html += """</p>
        </div>
    </div>
    """
    
    return html

def filter_data_by_date(df, start_date, end_date, date_column='Date'):
    """Filter data by date range."""
    if df is None or df.empty:
        print("Empty dataframe passed to filter_data_by_date")
        return df
    
    # Print columns for debugging
    print(f"Columns in dataframe: {df.columns.tolist()}")
    
    # Check if date column exists
    if date_column not in df.columns:
        print(f"Date column '{date_column}' not found in dataframe")
        # Try to find date columns
        date_cols = [col for col in df.columns if 'date' in col.lower()]
        if date_cols:
            date_column = date_cols[0]
            print(f"Using alternative date column: {date_column}")
        else:
            print("No date column found, returning unfiltered data")
            return df
    
    # Create a copy to avoid modification warnings
    filtered_df = df.copy()
    
    # Print sample dates for debugging
    print(f"Sample dates from column '{date_column}':")
    print(filtered_df[date_column].head())
    
    # Check current date format in the column
    # If all dates appear to be 1970-01-01 (Unix epoch), we need to handle this differently
    epoch_date_pattern = filtered_df[date_column].dt.year == 1970
    
    if epoch_date_pattern.all():
        print("WARNING: All dates appear to be from 1970 (Unix epoch start). This suggests a date parsing issue.")
        print("Skipping date filtering and returning all data.")
        return df
    
    # Make sure date column is datetime type
    if not pd.api.types.is_datetime64_any_dtype(filtered_df[date_column]):
        try:
            print(f"Converting {date_column} to datetime")
            filtered_df[date_column] = pd.to_datetime(filtered_df[date_column], errors='coerce')
            print(f"After conversion: {filtered_df[date_column].head()}")
        except Exception as e:
            print(f"Error converting dates: {str(e)}")
            return df
    
    # Get original row count
    original_count = len(filtered_df)
    
    # Convert input dates to datetime
    try:
        start_date_dt = pd.to_datetime(start_date)
        end_date_dt = pd.to_datetime(end_date)
        
        # Add one day to end_date to include the end date in the results
        end_date_dt = end_date_dt + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        
        print(f"Filtering data between {start_date_dt} and {end_date_dt}")
        
        # Apply filters
        filtered_df = filtered_df[(filtered_df[date_column] >= start_date_dt) & 
                                 (filtered_df[date_column] <= end_date_dt)]
    except Exception as e:
        print(f"Error applying date filters: {str(e)}")
        return df
    
    # Get filtered row count
    filtered_count = len(filtered_df)
    print(f"Filtered data: {filtered_count} rows (removed {original_count - filtered_count} rows)")
    
    # If we've filtered out all data, return the original data with a warning
    if filtered_count == 0:
        print("WARNING: All data filtered out, returning original data")
        return df
    
    return filtered_df