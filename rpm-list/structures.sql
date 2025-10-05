CREATE TABLE provides
(
  pkg_name character varying(100),
  pkg_version character varying(50),
  pkg_release character varying(50),
  pkg_size bigint,
  pro_name character varying(600),
  pro_equ character varying(5),
  pro_version character varying(50)
);
CREATE TABLE requires
(
  pkg_name character varying(100),
  pkg_version character varying(50),
  pkg_release character varying(50),
  req_name character varying(600),
  req_equ character varying(5),
  req_version character varying(50)
);