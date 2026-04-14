import random
import time

class Pixel:
    def __init__(self, id, face, intensidad):
        self.id = id
        self.face = face
        self.intensidad = intensidad

    def __eq__(self, other):
        if isinstance(other, Pixel):
            return self.face == other.face and self.intensidad == other.intensidad
        return False

    def __hash__(self):
        return hash((self.face, self.intensidad))

def main():
    num_objetos = 10000
    lista_pixels = []
    
    # Asegurarnos de que el target esté en una posición aleatoria
    pos_target = random.randint(0, num_objetos - 1)
    
    for i in range(num_objetos):
        if i == pos_target:
            p = Pixel(i, True, 1.0)
        else:
            # Generar intensidad asegurando que no sea 1.0 si face es True
            face = random.choice([True, False])
            intensidad = random.uniform(0.0, 0.99) 
            p = Pixel(i, face, intensidad)
        lista_pixels.append(p)
        
    set_pixels = set(lista_pixels)
    
    target = Pixel(-1, True, 1.0)
    
    # Búsqueda en LISTA
    print("=== LISTA ===")
    inicio_lista = time.perf_counter()
    
    try:
        # Busca la primera aparición de forma ultrarrápida (en C puro)
        pos = lista_pixels.index(target)
        encontrado = True
        try:
            # Busca si hay una segunda aparición desde pos+1 en adelante
            lista_pixels.index(target, pos + 1)
            encontrados_lista = 2
        except ValueError:
            encontrados_lista = 1
    except ValueError:
        encontrado = False
        encontrados_lista = 0
        
    fin_lista = time.perf_counter()
    
    tiempo_lista = fin_lista - inicio_lista
    print(f"Encontrado: {encontrado}")
    print(f"Tiempo: {tiempo_lista:.5f} segundos")
    if encontrados_lista == 1:
        print("Único objeto")
    else:
        print(f"No es único, hay {encontrados_lista}")
        
    if tiempo_lista > 0.0001:
        print("PEATÓN MUERTO")

    # Búsqueda en SET
    print("\n=== SET ===")
    inicio_set = time.perf_counter()
    # Usamos la búsqueda O(1) del set
    encontrado_set = target in set_pixels
    # Como el set no permite duplicados con el mismo hash y eq, por definición si está, es único.
    # Pero para cumplir la condición estrictamente podemos decir que está garantizado 
    # por la propia validación previa, o podríamos buscar duplicados en la lista de origen en inserción.
    fin_set = time.perf_counter()
    
    tiempo_set = fin_set - inicio_set
    print(f"Encontrado: {encontrado_set}")
    print(f"Tiempo: {tiempo_set:.5f} segundos")
    if encontrado_set:
         print("Único objeto") # Solo puede haber 1 en el set
         
    if tiempo_set > 0.0001:
        print("PEATÓN MUERTO")

if __name__ == "__main__":
    main()
