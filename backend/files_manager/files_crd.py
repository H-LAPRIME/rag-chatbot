import os

def create_file(file_object, folder_path):
    """
    Create a file in the specified folder from a file object.
    
    :param file_object: A file-like object (e.g., from Flask/Django request.files)
                        Must have 'filename' and 'read()' method.
    :param folder_path: Path to the folder where the file will be saved.
    :return: Full path of the created file.
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    file_path = os.path.join(folder_path, file_object.filename)
    
    with open(file_path, 'wb') as f:
        f.write(file_object.read())
    
    return file_path

def retrieve_file(file_name, folder_path):
    """
    Retrieve a file from the specified folder.
    
    :param file_name: Name of the file to retrieve.
    :param folder_path: Folder where the file is stored.
    :return: Full path if exists, else None
    """
    file_path = os.path.join(folder_path, file_name)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return file_path
    return None

def delete_file(file_name, folder_path):
    """
    Delete a file from the specified folder.
    
    :param file_name: Name of the file to delete.
    :param folder_path: Folder where the file is stored.
    :return: True if deleted, False if file does not exist.
    """
    file_path = os.path.join(folder_path, file_name)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        os.remove(file_path)
        return True
    return False


# Example usage (commented out for REST integration):
# from werkzeug.datastructures import FileStorage
# uploaded_file = FileStorage(stream=open('example.txt', 'rb'), filename='example.txt')
# folder = "./uploads"
# create_file(uploaded_file, folder)
# print(retrieve_file("example.txt", folder))
# print(delete_file("example.txt", folder))
