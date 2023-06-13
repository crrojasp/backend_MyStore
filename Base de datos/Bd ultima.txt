-- Table: public.carrito_compra

-- DROP TABLE IF EXISTS public.carrito_compra;

CREATE TABLE IF NOT EXISTS public.carrito_compra
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 200000 MINVALUE 200000 MAXVALUE 400000 CACHE 1 ),
    productos text[] COLLATE pg_catalog."default",
    id_comprador integer NOT NULL,
    CONSTRAINT carrito_compra_pkey PRIMARY KEY (id),
    CONSTRAINT carrito_compra_id_comprador_fkey FOREIGN KEY (id_comprador)
        REFERENCES public.comprador (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.carrito_compra
    OWNER to postgres;

-- Table: public.compra

-- DROP TABLE IF EXISTS public.compra;

CREATE TABLE IF NOT EXISTS public.compra
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 400001 MINVALUE 400001 MAXVALUE 600000 CACHE 1 ),
    fecha date NOT NULL,
    total numeric NOT NULL,
    estado character varying COLLATE pg_catalog."default",
    id_comprador integer NOT NULL,
    CONSTRAINT compra_pkey PRIMARY KEY (id),
    CONSTRAINT compra_id_comprador_fkey FOREIGN KEY (id_comprador)
        REFERENCES public.comprador (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.compra
    OWNER to postgres;

-- Table: public.comprador

-- DROP TABLE IF EXISTS public.comprador;

CREATE TABLE IF NOT EXISTS public.comprador
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 600001 MINVALUE 600001 MAXVALUE 800000 CACHE 1 ),
    direccion character varying COLLATE pg_catalog."default",
    telefono bigint,
    historial_compras text[] COLLATE pg_catalog."default",
    CONSTRAINT comprador_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.comprador
    OWNER to postgres;

-- Table: public.devolucion

-- DROP TABLE IF EXISTS public.devolucion;

CREATE TABLE IF NOT EXISTS public.devolucion
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 800001 MINVALUE 800001 MAXVALUE 1000000 CACHE 1 ),
    fecha_solicitud date NOT NULL,
    id_producto integer NOT NULL,
    id_vendedor integer NOT NULL,
    id_comprador integer NOT NULL,
    razon text COLLATE pg_catalog."default" NOT NULL,
    id_envio integer,
    CONSTRAINT devolucion_pkey PRIMARY KEY (id),
    CONSTRAINT devolucion_id_comprador_fkey FOREIGN KEY (id_comprador)
        REFERENCES public.comprador (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT devolucion_id_producto_fkey FOREIGN KEY (id_producto)
        REFERENCES public.producto (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT devolucion_id_vendedor_fkey FOREIGN KEY (id_vendedor)
        REFERENCES public.vendedor (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.devolucion
    OWNER to postgres;

-- Table: public.envio

-- DROP TABLE IF EXISTS public.envio;

CREATE TABLE IF NOT EXISTS public.envio
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1000001 MINVALUE 1000001 MAXVALUE 1200000 CACHE 1 ),
    direccion_entrega character varying COLLATE pg_catalog."default" NOT NULL,
    direccion_origen character varying COLLATE pg_catalog."default" NOT NULL,
    transportista character varying COLLATE pg_catalog."default",
    precio numeric NOT NULL,
    id_producto integer NOT NULL,
    CONSTRAINT envio_pkey PRIMARY KEY (id),
    CONSTRAINT envio_id_producto_fkey FOREIGN KEY (id_producto)
        REFERENCES public.producto (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.envio
    OWNER to postgres;

-- Table: public.lista_deseos

-- DROP TABLE IF EXISTS public.lista_deseos;

CREATE TABLE IF NOT EXISTS public.lista_deseos
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1200001 MINVALUE 1200001 MAXVALUE 1400000 CACHE 1 ),
    productos text[] COLLATE pg_catalog."default",
    id_comprador integer NOT NULL,
    CONSTRAINT lista_deseos_pkey PRIMARY KEY (id),
    CONSTRAINT lista_deseos_id_comprador_fkey FOREIGN KEY (id_comprador)
        REFERENCES public.comprador (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.lista_deseos
    OWNER to postgres;

-- Table: public.plantilla

-- DROP TABLE IF EXISTS public.plantilla;

CREATE TABLE IF NOT EXISTS public.plantilla
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1400001 MINVALUE 1400001 MAXVALUE 1600000 CACHE 1 ),
    nombre character varying(30) COLLATE pg_catalog."default" NOT NULL,
    descripcion text COLLATE pg_catalog."default" NOT NULL,
    secciones text[] COLLATE pg_catalog."default",
    "diseño" character varying COLLATE pg_catalog."default",
    tipo character varying COLLATE pg_catalog."default",
    url character varying COLLATE pg_catalog."default",
    CONSTRAINT plantilla_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.plantilla
    OWNER to postgres;

-- Table: public.producto

-- DROP TABLE IF EXISTS public.producto;

CREATE TABLE IF NOT EXISTS public.producto
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1600001 MINVALUE 1600001 MAXVALUE 1800000 CACHE 1 ),
    nombre character varying COLLATE pg_catalog."default" NOT NULL,
    descripcion text COLLATE pg_catalog."default",
    precio numeric NOT NULL,
    ilustracion bytea[],
    CONSTRAINT producto_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.producto
    OWNER to postgres;

-- Table: public.suscripcion

-- DROP TABLE IF EXISTS public.suscripcion;

CREATE TABLE IF NOT EXISTS public.suscripcion
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1800001 MINVALUE 1800001 MAXVALUE 2000000 CACHE 1 ),
    fecha_inicio date NOT NULL,
    fecha_fin date NOT NULL,
    precio numeric NOT NULL,
    tipo character varying COLLATE pg_catalog."default",
    id_usuario integer NOT NULL,
    CONSTRAINT suscripcion_pkey PRIMARY KEY (id),
    CONSTRAINT suscripcion_id_usuario_fkey FOREIGN KEY (id_usuario)
        REFERENCES public.usuario (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.suscripcion
    OWNER to postgres;

-- Table: public.tienda

-- DROP TABLE IF EXISTS public.tienda;

CREATE TABLE IF NOT EXISTS public.tienda
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 2000001 MINVALUE 2000001 MAXVALUE 2200001 CACHE 1 ),
    nombre character varying(50) COLLATE pg_catalog."default" NOT NULL,
    direccion character varying(50) COLLATE pg_catalog."default" NOT NULL,
    id_vendedor integer NOT NULL,
    productos text[] COLLATE pg_catalog."default",
    CONSTRAINT tienda_pkey PRIMARY KEY (id),
    CONSTRAINT tienda_id_vendedor_fkey FOREIGN KEY (id_vendedor)
        REFERENCES public.vendedor (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.tienda
    OWNER to postgres;

-- Table: public.usuario

-- DROP TABLE IF EXISTS public.usuario;

CREATE TABLE IF NOT EXISTS public.usuario
(
    name text COLLATE pg_catalog."default" NOT NULL,
    email text COLLATE pg_catalog."default" NOT NULL,
    cellphone text COLLATE pg_catalog."default" NOT NULL,
    password text COLLATE pg_catalog."default" NOT NULL,
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( CYCLE INCREMENT 1 START 0 MINVALUE 0 MAXVALUE 200000 CACHE 1 ),
    tipo text COLLATE pg_catalog."default",
    CONSTRAINT users_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.usuario
    OWNER to postgres;

-- Table: public.vendedor

-- DROP TABLE IF EXISTS public.vendedor;

CREATE TABLE IF NOT EXISTS public.vendedor
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 2200001 MINVALUE 2200001 MAXVALUE 2400000 CACHE 1 ),
    nombre_tienda character varying(30) COLLATE pg_catalog."default" NOT NULL,
    rues integer,
    historial_ventas text[] COLLATE pg_catalog."default",
    nombre character varying(30) COLLATE pg_catalog."default",
    CONSTRAINT vendedor_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.vendedor
    OWNER to postgres;

-- Table: public.venta

-- DROP TABLE IF EXISTS public.venta;

CREATE TABLE IF NOT EXISTS public.venta
(
    id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( CYCLE INCREMENT 1 START 2400001 MINVALUE 2400001 MAXVALUE 2600000 CACHE 1 ),
    fecha date NOT NULL,
    total double precision NOT NULL,
    estado character varying COLLATE pg_catalog."default" NOT NULL,
    id_vendedor integer NOT NULL,
    productos text[] COLLATE pg_catalog."default",
    CONSTRAINT venta_pkey PRIMARY KEY (id),
    CONSTRAINT venta_id_vendedor_fkey FOREIGN KEY (id_vendedor)
        REFERENCES public.vendedor (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.venta
    OWNER to postgres;