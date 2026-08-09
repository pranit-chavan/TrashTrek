"""
TrashTrek Web Dashboard
Interactive web-based interface with map visualization and dynamic optimization
"""

from flask import Flask, render_template, request, jsonify, session
from trashtrek import SmartBinOptimizer, MultiTruckOptimizer, Bin
import json
import os
import requests
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Data storage directory
DATA_DIR = "saved_configs"
os.makedirs(DATA_DIR, exist_ok=True)

def get_osrm_distance_matrix(coords):
    """
    coords: list of dicts with 'lat' and 'lng'
    Returns a 2D distance matrix in km using OSRM Table API
    """
    coord_str = ";".join([f"{c['lng']},{c['lat']}" for c in coords])
    url = f"http://router.project-osrm.org/table/v1/driving/{coord_str}?annotations=distance"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get('code') == 'Ok':
            # distances are in meters, convert to km
            matrix = []
            for row in data['distances']:
                km_row = [round(d / 1000.0, 2) if d is not None else 0.0 for d in row]
                matrix.append(km_row)
            return matrix
        else:
            print("OSRM Error:", data)
            return None
    except Exception as e:
        print("Error fetching OSRM distances:", e)
        return None


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/optimize', methods=['POST'])
def optimize_route():
    """Run optimization algorithm and return results"""
    try:
        data = request.json
        
        # Extract parameters
        bins_data = data.get('bins', [])
        truck_capacity = data.get('truck_capacity', 150)
        num_trucks = data.get('num_trucks', 1)
        coordinates = data.get('coordinates', None)
        distance_matrix = data.get('distance_matrix', None)
        
        # Override with real distances if coordinates are provided
        if coordinates and len(coordinates) > 1:
            osrm_matrix = get_osrm_distance_matrix(coordinates)
            if osrm_matrix:
                distance_matrix = osrm_matrix
        
        # Create bins
        bins = []
        for i, bin_data in enumerate(bins_data):
            if bin_data.get('weight', 0) > 0:  # Only include bins with garbage
                bins.append(Bin(
                    id=i,
                    fill_level=bin_data.get('fill_level', 50),
                    weight=int(bin_data.get('weight', 0))
                ))
        
        if not bins:
            return jsonify({
                'success': False,
                'error': 'No bins with garbage to collect'
            })
        
        # Run optimization
        if num_trucks > 1:
            optimizer = MultiTruckOptimizer(
                num_bins=len(bins),
                truck_capacity=truck_capacity,
                num_trucks=num_trucks,
                distance_matrix=distance_matrix
            )
            optimizer.bins = bins
            
            # Get results for each truck
            results = []
            remaining_bins = bins.copy()
            
            for truck_num in range(num_trucks):
                if not remaining_bins:
                    break
                
                optimizer.bins = remaining_bins
                selected_bins, total_weight = optimizer.knapsack_bin_selection()
                
                if not selected_bins:
                    break
                
                route, total_distance = optimizer.optimize_route(selected_bins)
                
                results.append({
                    'truck_id': truck_num + 1,
                    'selected_bins': [{'id': b.id, 'weight': b.weight, 'fill_level': b.fill_level} for b in selected_bins],
                    'total_weight': total_weight,
                    'route': route,
                    'total_distance': round(total_distance, 2)
                })
                
                # Remove selected bins
                selected_ids = {b.id for b in selected_bins}
                remaining_bins = [b for b in remaining_bins if b.id not in selected_ids]
            
            return jsonify({
                'success': True,
                'mode': 'multi_truck',
                'results': results,
                'total_trucks_used': len(results),
                'total_weight': sum(r['total_weight'] for r in results),
                'total_distance': sum(r['total_distance'] for r in results)
            })
        
        else:
            # Single truck optimization
            optimizer = SmartBinOptimizer(
                num_bins=len(bins),
                truck_capacity=truck_capacity,
                distance_matrix=distance_matrix
            )
            optimizer.bins = bins
            
            selected_bins, total_weight = optimizer.knapsack_bin_selection()
            
            if not selected_bins:
                return jsonify({
                    'success': False,
                    'error': 'Truck capacity too small for any bin'
                })
            
            route, total_distance = optimizer.optimize_route(selected_bins)
            
            # Calculate efficiency
            efficiency = total_weight / total_distance if total_distance > 0 else 0
            capacity_utilization = (total_weight / truck_capacity) * 100
            
            return jsonify({
                'success': True,
                'mode': 'single_truck',
                'selected_bins': [{'id': b.id, 'weight': b.weight, 'fill_level': b.fill_level} for b in selected_bins],
                'skipped_bins': [{'id': b.id, 'weight': b.weight, 'fill_level': b.fill_level} for b in bins if b not in selected_bins],
                'total_weight': total_weight,
                'route': route,
                'total_distance': round(total_distance, 2),
                'efficiency': round(efficiency, 2),
                'capacity_utilization': round(capacity_utilization, 1),
                'distance_matrix': optimizer.distance_matrix
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/save_config', methods=['POST'])
def save_config():
    """Save current configuration to file"""
    try:
        data = request.json
        config_name = data.get('name', f'config_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        
        # Sanitize filename
        config_name = "".join(c for c in config_name if c.isalnum() or c in (' ', '_', '-')).strip()
        
        filepath = os.path.join(DATA_DIR, f"{config_name}.json")
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': f'Configuration saved as {config_name}',
            'filename': config_name
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/load_config/<filename>', methods=['GET'])
def load_config(filename):
    """Load configuration from file"""
    try:
        filepath = os.path.join(DATA_DIR, f"{filename}.json")
        
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': 'Configuration not found'
            })
        
        with open(filepath, 'r') as f:
            config = json.load(f)
        
        return jsonify({
            'success': True,
            'config': config
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/list_configs', methods=['GET'])
def list_configs():
    """List all saved configurations"""
    try:
        configs = []
        for filename in os.listdir(DATA_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(DATA_DIR, filename)
                stat = os.stat(filepath)
                configs.append({
                    'name': filename[:-5],  # Remove .json
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'size': stat.st_size
                })
        
        configs.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({
            'success': True,
            'configs': configs
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/delete_config/<filename>', methods=['DELETE'])
def delete_config(filename):
    """Delete a saved configuration"""
    try:
        filepath = os.path.join(DATA_DIR, f"{filename}.json")
        
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({
                'success': True,
                'message': f'Configuration {filename} deleted'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Configuration not found'
            })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("TRASHTREK")
    print("=" * 70)
    print("\nStarting server...")
    print("Open your browser and go to: http://localhost:5000")
    print("\nFeatures:")
    print("  * Interactive map visualization")
    print("  * Dynamic route optimization")
    print("  * Real-time result dashboard")
    print("  * Save/Load configurations")
    print("  * Multi-truck support")
    print("\nPress Ctrl+C to stop the server\n")
    print("=" * 70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
