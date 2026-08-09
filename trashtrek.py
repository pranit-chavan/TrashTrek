"""
♻️ SmartBin++: Intelligent Waste Collection Route Optimizer
A DSA-based system for optimizing waste collection routes using:
- 0/1 Knapsack (Dynamic Programming) for bin selection
- Dijkstra's Algorithm for shortest path routing
- Greedy heuristics for route optimization
"""

import random
import heapq
from typing import List, Tuple, Dict, Set
from dataclasses import dataclass


@dataclass
class Bin:
    """Represents a smart waste bin with fill level and weight data"""
    id: int
    fill_level: int  # Percentage (0-100)
    weight: int      # Weight in kg
    
    def __repr__(self):
        return f"Bin {self.id}: Fill={self.fill_level}%, Weight={self.weight}kg"


class SmartBinOptimizer:
    """Main class for waste collection route optimization"""
    
    def __init__(self, num_bins: int, truck_capacity: int, distance_matrix: List[List[float]] = None):
        """
        Initialize the SmartBin++ system
        
        Args:
            num_bins: Number of waste bins in the city
            truck_capacity: Maximum weight capacity of the truck (kg)
            distance_matrix: Optional adjacency matrix for distances between bins
        """
        self.num_bins = num_bins
        self.truck_capacity = truck_capacity
        self.bins: List[Bin] = []
        self.distance_matrix = distance_matrix
        
        # Generate bins and distance matrix if not provided
        self._generate_bins()
        if self.distance_matrix is None:
            self._generate_distance_matrix()
    
    def _generate_bins(self):
        """Generate random bin data for simulation"""
        for i in range(self.num_bins):
            fill_level = random.randint(30, 100)
            weight = random.randint(20, 80)
            self.bins.append(Bin(id=i, fill_level=fill_level, weight=weight))
    
    def _generate_distance_matrix(self):
        """Generate random distance matrix representing city map"""
        # Create symmetric distance matrix
        n = self.num_bins + 2  # +2 for start depot and dump yard
        self.distance_matrix = [[0.0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(i + 1, n):
                # Random distance between 1 and 10 km
                distance = round(random.uniform(1.0, 10.0), 1)
                self.distance_matrix[i][j] = distance
                self.distance_matrix[j][i] = distance
    
    def knapsack_bin_selection(self) -> Tuple[List[Bin], int]:
        """
        Route-aware bin selection using greedy approach with distance consideration
        Selects bins to maximize efficiency (weight collected per km traveled)
        
        Returns:
            Tuple of (selected_bins, total_weight)
        """
        if not self.bins:
            return [], 0
        
        # Start with all bins that have garbage
        available_bins = [b for b in self.bins if b.weight > 0]
        
        if not available_bins:
            return [], 0
        
        selected_bins = []
        total_weight = 0
        remaining_capacity = self.truck_capacity
        current_location = 0  # Start depot
        
        # Greedy selection: pick bins based on efficiency (weight/distance ratio)
        while available_bins and remaining_capacity > 0:
            best_bin = None
            best_efficiency = -1
            best_distance = float('inf')
            
            for bin in available_bins:
                if bin.weight <= remaining_capacity:
                    # Calculate distance from current location to this bin
                    bin_node = bin.id + 1  # Bins are at indices 1 to n
                    distance = self.distance_matrix[current_location][bin_node]
                    
                    if distance > 0:
                        # Efficiency = weight / distance (higher is better)
                        # Also consider fill level as priority
                        efficiency = (bin.weight * bin.fill_level / 100) / distance
                        
                        # Prefer higher efficiency
                        if efficiency > best_efficiency:
                            best_efficiency = efficiency
                            best_bin = bin
                            best_distance = distance
            
            # If we found a good bin, select it
            if best_bin:
                selected_bins.append(best_bin)
                total_weight += best_bin.weight
                remaining_capacity -= best_bin.weight
                current_location = best_bin.id + 1  # Update current location
                available_bins.remove(best_bin)
            else:
                # No more bins fit or no more bins available
                break
        
        return selected_bins, total_weight
    
    def dijkstra_shortest_path(self, start: int, end: int) -> Tuple[float, List[int]]:
        """
        Find shortest path between two nodes using Dijkstra's algorithm
        
        Args:
            start: Starting node index
            end: Ending node index
            
        Returns:
            Tuple of (distance, path)
        """
        n = len(self.distance_matrix)
        distances = [float('inf')] * n
        distances[start] = 0
        previous = [-1] * n
        visited = set()
        
        # Min-heap: (distance, node)
        pq = [(0, start)]
        
        while pq:
            current_dist, u = heapq.heappop(pq)
            
            if u in visited:
                continue
            
            visited.add(u)
            
            if u == end:
                break
            
            for v in range(n):
                if v not in visited and self.distance_matrix[u][v] > 0:
                    new_dist = current_dist + self.distance_matrix[u][v]
                    
                    if new_dist < distances[v]:
                        distances[v] = new_dist
                        previous[v] = u
                        heapq.heappush(pq, (new_dist, v))
        
        # Reconstruct path
        path = []
        current = end
        while current != -1:
            path.append(current)
            current = previous[current]
        path.reverse()
        
        return distances[end], path
    
    def optimize_route(self, selected_bins: List[Bin]) -> Tuple[List[int], float]:
        """
        Find optimal visiting order for selected bins using greedy nearest neighbor
        
        Args:
            selected_bins: List of bins to visit
            
        Returns:
            Tuple of (route, total_distance)
        """
        if not selected_bins:
            return [], 0.0
        
        # Node indices: 0 = start depot, 1..n = bins, n+1 = dump yard
        start_depot = 0
        dump_yard = self.num_bins + 1
        
        # Map bin IDs to node indices (bins are at indices 1 to num_bins)
        bin_nodes = [bin.id + 1 for bin in selected_bins]
        
        # Greedy nearest neighbor algorithm
        route = [start_depot]
        unvisited = set(bin_nodes)
        current = start_depot
        total_distance = 0.0
        
        while unvisited:
            # Find nearest unvisited bin
            nearest = min(unvisited, key=lambda node: self.distance_matrix[current][node])
            distance = self.distance_matrix[current][nearest]
            
            route.append(nearest)
            total_distance += distance
            current = nearest
            unvisited.remove(nearest)
        
        # Return to dump yard
        route.append(dump_yard)
        total_distance += self.distance_matrix[current][dump_yard]
        
        return route, total_distance
    
    def run_optimization(self) -> Dict:
        """
        Execute complete optimization pipeline
        
        Returns:
            Dictionary containing optimization results
        """
        print("♻️  SmartBin++: Waste Collection Optimization\n")
        
        # Display bin data
        print("Generated Bin Data:")
        for bin in self.bins:
            print(f"  {bin}")
        print()
        
        # Step 1: Select bins using route-aware greedy algorithm
        selected_bins, total_weight = self.knapsack_bin_selection()
        
        print(f"Selected {len(selected_bins)} bins for collection:")
        for bin in selected_bins:
            print(f"  → Bin {bin.id} | Weight={bin.weight}kg | Fill={bin.fill_level}%")
        print()
        
        # Step 2: Optimize route
        route, total_distance = self.optimize_route(selected_bins)
        
        print(f"Total Waste Collected: {total_weight} kg")
        
        # Format route for display
        route_names = []
        for node in route:
            if node == 0:
                route_names.append("Start")
            elif node == self.num_bins + 1:
                route_names.append("Dump Yard")
            else:
                route_names.append(f"Bin{node-1}")
        
        print(f"Optimal Route: {' → '.join(route_names)}")
        print(f"Total Distance: {total_distance:.1f} km")
        print("\n✅ SmartBin++ Optimization Complete!\n")
        
        return {
            'selected_bins': selected_bins,
            'total_weight': total_weight,
            'route': route,
            'route_names': route_names,
            'total_distance': total_distance
        }


class MultiTruckOptimizer(SmartBinOptimizer):
    """Extended optimizer supporting multiple trucks"""
    
    def __init__(self, num_bins: int, truck_capacity: int, num_trucks: int = 1, 
                 distance_matrix: List[List[float]] = None):
        super().__init__(num_bins, truck_capacity, distance_matrix)
        self.num_trucks = num_trucks
    
    def run_multi_truck_optimization(self) -> List[Dict]:
        """
        Run optimization for multiple trucks
        
        Returns:
            List of optimization results for each truck
        """
        print(f"♻️  SmartBin++: Multi-Truck Optimization ({self.num_trucks} trucks)\n")
        
        # Display bin data
        print("Generated Bin Data:")
        for bin in self.bins:
            print(f"  {bin}")
        print()
        
        results = []
        remaining_bins = self.bins.copy()
        
        for truck_num in range(self.num_trucks):
            if not remaining_bins:
                break
            
            print(f"\n🚛 Truck {truck_num + 1} Optimization:")
            print("-" * 50)
            
            # Temporarily set bins to remaining bins
            original_bins = self.bins
            self.bins = remaining_bins
            
            # Select bins for this truck
            selected_bins, total_weight = self.knapsack_bin_selection()
            
            if not selected_bins:
                self.bins = original_bins
                break
            
            print(f"Selected {len(selected_bins)} bins:")
            for bin in selected_bins:
                print(f"  → Bin {bin.id} | Weight={bin.weight}kg | Fill={bin.fill_level}%")
            
            # Optimize route
            route, total_distance = self.optimize_route(selected_bins)
            
            # Format route
            route_names = []
            for node in route:
                if node == 0:
                    route_names.append("Start")
                elif node == self.num_bins + 1:
                    route_names.append("Dump Yard")
                else:
                    route_names.append(f"Bin{node-1}")
            
            print(f"Total Waste: {total_weight} kg")
            print(f"Route: {' → '.join(route_names)}")
            print(f"Distance: {total_distance:.1f} km")
            
            results.append({
                'truck_id': truck_num + 1,
                'selected_bins': selected_bins,
                'total_weight': total_weight,
                'route': route,
                'route_names': route_names,
                'total_distance': total_distance
            })
            
            # Remove selected bins from remaining
            selected_ids = {bin.id for bin in selected_bins}
            remaining_bins = [bin for bin in remaining_bins if bin.id not in selected_ids]
            
            # Restore original bins
            self.bins = original_bins
        
        print("\n" + "=" * 50)
        print("✅ Multi-Truck Optimization Complete!")
        print(f"Total trucks used: {len(results)}")
        total_collected = sum(r['total_weight'] for r in results)
        total_distance = sum(r['total_distance'] for r in results)
        print(f"Total waste collected: {total_collected} kg")
        print(f"Total distance traveled: {total_distance:.1f} km\n")
        
        return results


def main():
    """Example usage of SmartBin++"""
    
    # Example 1: Single truck optimization
    print("=" * 60)
    print("EXAMPLE 1: Single Truck Optimization")
    print("=" * 60 + "\n")
    
    optimizer = SmartBinOptimizer(
        num_bins=6,
        truck_capacity=150
    )
    result = optimizer.run_optimization()
    
    # Example 2: Multi-truck optimization
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Multi-Truck Optimization")
    print("=" * 60 + "\n")
    
    multi_optimizer = MultiTruckOptimizer(
        num_bins=10,
        truck_capacity=120,
        num_trucks=3
    )
    results = multi_optimizer.run_multi_truck_optimization()
    
    # Example 3: Custom distance matrix
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Custom City Map")
    print("=" * 60 + "\n")
    
    # Custom 4-bin scenario with specific distances
    custom_distances = [
        [0.0, 2.5, 5.0, 7.5, 3.0, 8.0],  # Start depot
        [2.5, 0.0, 3.0, 6.0, 4.5, 5.5],  # Bin 0
        [5.0, 3.0, 0.0, 4.0, 6.0, 3.5],  # Bin 1
        [7.5, 6.0, 4.0, 0.0, 5.5, 2.0],  # Bin 2
        [3.0, 4.5, 6.0, 5.5, 0.0, 7.0],  # Bin 3
        [8.0, 5.5, 3.5, 2.0, 7.0, 0.0],  # Dump yard
    ]
    
    custom_optimizer = SmartBinOptimizer(
        num_bins=4,
        truck_capacity=140,
        distance_matrix=custom_distances
    )
    custom_result = custom_optimizer.run_optimization()


if __name__ == "__main__":
    import sys
    
    # Check if user wants interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        print("\n🔄 Launching interactive mode...")
        print("Please run: python interactive.py\n")
    else:
        main()
