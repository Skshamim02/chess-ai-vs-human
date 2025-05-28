def get_preprocessing_nodes(data):
    """
    Preprocess input data for the chess game.
    
    Args:
        data (list): A list of moves or raw data to preprocess.
        
    Returns:
        list: A list of preprocessed data.
    """
    preprocessed_data = []
    
    for item in data:
        # Skip invalid entries
        if not isinstance(item, str):
            continue
        
        # Basic preprocessing: strip whitespace and convert to lowercase
        cleaned_item = item.strip().lower()
        
        # Ensure the move is valid length (e.g., "e2e4")
        if len(cleaned_item) >= 4:
            preprocessed_data.append(cleaned_item)
    
    return preprocessed_data


# Example usage
if __name__ == "__main__":
    # Sample data
    sample_moves = [" e2e4 ", "d7d5", "a1 a3", None, 123, "invalid_move"]
    
    # Get preprocessed moves
    print("Preprocessed Moves:", get_preprocessing_nodes(sample_moves))
