"""Prueba de migración con datos heredados en una base MySQL vacía y desechable.

Uso desde backend: MIGRATION_TEST_DATABASE_URL=mysql+pymysql://.../pasajes_migration_test \
    python ../scripts/verificar_migracion.py
"""
import os
from pathlib import Path
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from alembic import command
from alembic.config import Config


def main():
    url = os.environ['MIGRATION_TEST_DATABASE_URL']
    parsed = make_url(url)
    if not parsed.drivername.startswith('mysql') or not (parsed.database or '').endswith('_migration_test'):
        raise SystemExit('Use exclusivamente una base MySQL desechable con sufijo _migration_test')
    engine = create_engine(url)
    if inspect(engine).get_table_names():
        raise SystemExit('La base de prueba debe estar vacía; no se modificó su contenido')
    os.environ['DATABASE_URL'] = url
    backend = Path(__file__).resolve().parents[1] / 'backend'
    config = Config(str(backend / 'alembic.ini'))
    config.set_main_option('script_location', str(backend / 'alembic'))
    command.upgrade(config, 'a7c3e9d2f104')
    with engine.begin() as db:
        db.execute(text("INSERT INTO cooperativas (id,nombre) VALUES (1,'Prueba de migracion')"))
        db.execute(text("INSERT INTO usuarios (id,nombre,correo,cedula,rol,activo) VALUES (1,'Pasajero prueba','migracion@example.test','123456789012345','cliente',1)"))
        db.execute(text("INSERT INTO buses (id,placa,numero_disco,capacidad_asientos,cooperativa_id,activo) VALUES (1,'TEST-001','1',10,1,1)"))
        db.execute(text("INSERT INTO rutas (id,origen,destino,duracion_estimada_horas,activo) VALUES (1,'Quito','Cuenca',8,1)"))
        db.execute(text("INSERT INTO frecuencias (id,ruta_id,bus_id,hora_salida,precio,activo) VALUES (1,1,1,'10:00:00',20,1)"))
        for asiento, estado in enumerate(['PENDIENTE','CANCELADA','EXPIRADA'], 1):
            db.execute(text("INSERT INTO reservas (id,usuario_id,frecuencia_id,fecha_viaje,asiento,tipo_pasajero,precio,estado) VALUES (:id,1,1,'2030-01-01',:id,'GENERAL',20,:estado)"), {'id':asiento,'estado':estado})
    command.upgrade(config, 'head')
    command.check(config)
    with engine.connect() as db:
        filas = db.execute(text('SELECT origen_orden,destino_orden,pasajero_cedula FROM reservas')).all()
        assert len(filas) == 3 and all(tuple(f) == (0,1,'123456789012345') for f in filas)
        assert db.scalar(text('SELECT COUNT(*) FROM ocupaciones_asientos')) == 1
        assert db.scalar(text('SELECT activo FROM frecuencias WHERE id=1')) == 0
    print('Migración verificada: datos preservados, ocupación migrada y esquema consistente.')
    engine.dispose()


if __name__ == '__main__':
    main()
