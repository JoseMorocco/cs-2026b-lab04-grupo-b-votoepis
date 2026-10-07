from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Users
from diagrams.onprem.network import Nginx
from diagrams.programming.framework import Django
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.monitoring import Grafana

graph_attr = {"fontsize": "20", "bgcolor": "white", "pad": "0.3"}

with Diagram("VotoEPIS - Vista de despliegue", filename="img/despliegue", show=False, direction="LR", graph_attr=graph_attr):
    usuarios = Users("Estudiantes y\nComité Electoral")
    
    with Cluster("Servidor en la nube (VPS)"):
        proxy = Nginx("Nginx\n(HTTPS)")
        
        with Cluster("Monolito en capas"):
            app = Django("VotoEPIS App\n(API + Lógica)")
        
        db = PostgreSQL("PostgreSQL\n(Padrón y Votos)")
        monitoreo = Grafana("Monitoreo")
        
    usuarios >> Edge(label="HTTPS") >> proxy >> app
    app >> Edge(label="Transacciones ACID") >> db
    app >> Edge(label="Auditoría / Logs", style="dotted") >> monitoreo