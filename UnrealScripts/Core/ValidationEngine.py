class ValidationEngine:
    def __init__(self):
        pass
    
    def validate_predictions(self, metadata, actual_stats):        
        predicted_polys = metadata['polygons']
        actual_polys = actual_stats['triangles']
        poly_error = abs(predicted_polys - actual_polys) / predicted_polys * 100 if predicted_polys > 0 else 0
        
        predicted_complexity = metadata['complexity']
        actual_memory = actual_stats['memory_mb']
        actual_complexity = self._classify_complexity(actual_memory)
        
        accuracy_score = 100 - poly_error
        
        return {
            'poly_error': poly_error,
            'accuracy_score': accuracy_score,
            'predicted_complexity': predicted_complexity,
            'actual_complexity': actual_complexity,
            'memory_mb': actual_memory
        }
    
    def _classify_complexity(self, memory_mb):
        if memory_mb <= 1:
            return "Low"
        elif memory_mb <= 5:
            return "Medium"
        elif memory_mb <= 20:
            return "High"
        else:
            return "Very High"