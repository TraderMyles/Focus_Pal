import shutil

# This will create lambda_function.zip with the *contents* of package/
shutil.make_archive("lambda_function", 'zip', root_dir="package")
