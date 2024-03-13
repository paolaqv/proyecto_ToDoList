from app import app, db
from app.modelos import Usuario, Categoria, Estado, RegistroTarea

if __name__ == '__main__':
   
    app.run(debug=True)
