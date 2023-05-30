/*==============================================================*/
/* DBMS name:      Base de datos V 1.0                          */
/* Created on:     10/03/2023                                   */
/*==============================================================*/


drop index ESCRIBEN2_FKEY;

drop table COMENTARIO;

drop index ENVIARSE_FKEY;

drop index COMPRA_PKEY;

drop table COMPRA;

drop index POSEE_FKEY;

drop table EMPRESA;

drop index ENVIO_PKEY;

drop table ENVIO;

drop index MYSTORE_PKEY;

drop table MYSTORE;

drop index POSEE2_FKEY;

drop table PRODUCTO;

drop index TIENE_FKEY;

drop table USUARIOVENDEDOR;

/*==============================================================*/
/* Table: COMENTARIO                                            */
/*==============================================================*/
create table COMENTARIO (
   IDTIENDA             INT4                 not null,
   IDCOMENTARIO         INT4                 not null,
   DESCRIPCIONCOMENTARIO VARCHAR(250)         not null
);

/*==============================================================*/
/* Index: ESCRIBEN2_FKEY                                        */
/*==============================================================*/
create  index ESCRIBEN2_FKEY on COMENTARIO (
IDTIENDA
);

/*==============================================================*/
/* Table: COMPRA                                                */
/*==============================================================*/
create table COMPRA (
   IDCOMPRA             INT4                 not null,
   IDENVIO              INT4                 not null,
   FECHACOMPRA          DATE                 not null,
   constraint PK_COMPRA primary key (IDCOMPRA)
);

/*==============================================================*/
/* Index: COMPRA_PKEY                                           */
/*==============================================================*/
create unique index COMPRA_PKEY on COMPRA (
IDCOMPRA
);

/*==============================================================*/
/* Index: ENVIARSE_FKEY                                         */
/*==============================================================*/
create  index ENVIARSE_FKEY on COMPRA (
IDENVIO
);

/*==============================================================*/
/* Table: EMPRESA                                               */
/*==============================================================*/
create table EMPRESA (
   IDTIENDA             INT4                 not null,
   URLTIENDA            VARCHAR(100)         null,
   PERSONALIZACION      Codigo               null,
   SERVIDOR             VARCHAR(200)         not null,
   RUT                  INT4                 not null,
   NOMBREEMPRESA        VARCHAR(25)          not null,
   RAZONSOCIAL          VARCHAR(25)          not null,
   constraint AK_IDTIENDA_EMPRESA unique (IDTIENDA)
);

/*==============================================================*/
/* Index: POSEE_FKEY                                            */
/*==============================================================*/
create  index POSEE_FKEY on EMPRESA (
SERVIDOR
);

/*==============================================================*/
/* Table: ENVIO                                                 */
/*==============================================================*/
create table ENVIO (
   IDENVIO              INT4                 not null,
   FECHAENVIO           DATE                 not null,
   PRECIO               DECIMAL              not null,
   EMPRESAENVIO         VARCHAR(50)          not null,
   constraint PK_ENVIO primary key (IDENVIO)
);

/*==============================================================*/
/* Index: ENVIO_PKEY                                            */
/*==============================================================*/
create unique index ENVIO_PKEY on ENVIO (
IDENVIO
);

/*==============================================================*/
/* Table: MYSTORE                                               */
/*==============================================================*/
create table MYSTORE (
   SERVIDOR             VARCHAR(200)         not null,
   constraint PK_MYSTORE primary key (SERVIDOR)
);

/*==============================================================*/
/* Index: MYSTORE_PKEY                                          */
/*==============================================================*/
create unique index MYSTORE_PKEY on MYSTORE (
SERVIDOR
);

/*==============================================================*/
/* Table: PRODUCTO                                              */
/*==============================================================*/
create table PRODUCTO (
   IDTIENDA             INT4                 not null,
   URLTIENDA            VARCHAR(100)         null,
   PERSONALIZACION      Codigo               null,
   SERVIDOR             VARCHAR(200)         not null,
   CODPRODUCTO          INT4                 not null,
   NOMBREPRODUCTO       VARCHAR(25)          not null,
   PRECIOPRODUCTO       DECIMAL              not null,
   DESCRIPCIONPRODUCTO  VARCHAR(25)          not null,
   IMAGENPRODUCTO       CHAR(254)            not null,
   constraint AK_IDTIENDA_PRODUCTO unique (IDTIENDA)
);

/*==============================================================*/
/* Index: POSEE2_FKEY                                           */
/*==============================================================*/
create  index POSEE2_FKEY on PRODUCTO (
SERVIDOR
);

/*==============================================================*/
/* Table: USUARIOVENDEDOR                                       */
/*==============================================================*/
create table USUARIOVENDEDOR (
   CORREOUSUARIO        VARCHAR(100)         not null,
   NOMBREUSUARIO        VARCHAR(25)          null,
   SNOMBREUSUARIO       VARCHAR(50)          null,
   APELLIDOUSUARIO      VARCHAR(25)          null,
   SAPELLIDOUSUARIO     VARCHAR(50)          null,
   TIPO                 BOOL                 null,
   SERVIDOR             VARCHAR(200)         not null,
   CEDULA               VARCHAR(12)          not null,
   CEDULAF              CHAR(254)            not null,
   FOTO                 CHAR(254)            not null,
   constraint AK_CORREOUSUARIO_USUARIOV unique (CORREOUSUARIO)
);

/*==============================================================*/
/* Index: TIENE_FKEY                                            */
/*==============================================================*/
create  index TIENE_FKEY on USUARIOVENDEDOR (
SERVIDOR
);

alter table COMENTARIO
   add constraint FK_COMENTAR_ESCRIBEN_EMPRESA foreign key (IDTIENDA)
      references EMPRESA (IDTIENDA)
      on delete restrict on update restrict;

alter table COMENTARIO
   add constraint FK_COMENTAR_ESCRIBEN2_PRODUCTO foreign key (IDTIENDA)
      references PRODUCTO (IDTIENDA)
      on delete restrict on update restrict;

alter table COMPRA
   add constraint FK_COMPRA_ENVIARSE_ENVIO foreign key (IDENVIO)
      references ENVIO (IDENVIO)
      on delete restrict on update restrict;

alter table EMPRESA
   add constraint FK_EMPRESA_POSEE_MYSTORE foreign key (SERVIDOR)
      references MYSTORE (SERVIDOR)
      on delete restrict on update restrict;

alter table PRODUCTO
   add constraint FK_PRODUCTO_POSEE2_MYSTORE foreign key (SERVIDOR)
      references MYSTORE (SERVIDOR)
      on delete restrict on update restrict;

alter table USUARIOVENDEDOR
   add constraint FK_USUARIOV_TIENE_MYSTORE foreign key (SERVIDOR)
      references MYSTORE (SERVIDOR)
      on delete restrict on update restrict;
