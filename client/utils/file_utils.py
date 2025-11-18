def format_file_size(bytes_val: int) -> str:
    """Format file size for display."""
    if not bytes_val or bytes_val <= 0:
        return ""
    
    if bytes_val < 1024:
        return f"{bytes_val} B"
    
    if bytes_val < 1024 * 1024:
        return f"{bytes_val / 1024:.1f} KB"
    
    return f"{bytes_val / (1024 * 1024):.1f} MB"
