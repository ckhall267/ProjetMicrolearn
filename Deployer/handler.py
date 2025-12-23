import os

def check_torch_model_archiver():
    # Vérifie si torch-model-archiver est installé
    try:
        import model_archiver
        return True
    except ImportError:
        return False

def create_model_archive(model_name, model_file, handler_file):
    """
    Simultation de la création d'un .mar pour TorchServe
    """
    output_path = f"{model_name}.mar"
    print(f"Creating archive for {model_name} at {output_path}...")
    # Ici, on appellerait : torch-model-archiver --model-name ...
    return output_path
