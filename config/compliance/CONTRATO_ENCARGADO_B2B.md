# Plantilla — Contrato de Encargo (B2B) · METGO 3D SpA

> **Borrador orientativo** para revisión legal externa. No constituye asesoría jurídica.  
> Completar campos `[…]` y anexar medidas técnicas vigentes (RAT, runbooks).

## Partes

- **Responsable:** `[Razón social cliente]`, RUT `[…]`, domicilio `[…]` (“Cliente”).  
- **Encargado:** METGO 3D SpA (“METGO”), contacto DPD: miguel.lucero@metgo3d.com.

## 1. Objeto

METGO trata datos personales **por cuenta del Cliente** al prestar la plataforma `[producto: Quillota / SPATI / VENTORA / …]` según instrucciones documentadas.

## 2. Datos e interesados

Categorías: `[operadores / contactos / …]`.  
Datos: `[nombre, email, teléfono, RUT, …]`.  
No se incluye tratamiento de categorías especiales salvo anexo.

## 3. Finalidad e instrucciones

Solo: autenticación, operación del servicio contratado, soporte, seguridad y cumplimiento legal.  
Prohibido: marketing propio de METGO con datos del Cliente sin instrucción escrita.

## 4. Duración

Desde `[fecha]` hasta fin del contrato de servicio + plazos de borrado (`[90]` días salvo obligación legal).

## 5. Obligaciones de METGO (Encargado)

1. Tratar solo según instrucciones documentadas del Cliente.  
2. Confidencialidad del personal con acceso.  
3. Medidas de seguridad proporcionales (cifrado PII, HTTPS, RLS, secretos en servidor, MFA admin).  
4. No subencargar sin aviso; subencargados típicos: hosting API, base de datos, CDN, correo (listar en anexo).  
5. Asistir al Cliente en derechos de titulares y brechas (aviso sin dilación injustificada; ventana técnica &lt; 4 h containment).  
6. Al término: devolver o borrar/anonimizar según instrucción, con certificación razonable.  
7. Poner a disposición información para auditorías acordadas (sin comprometer secretos de otros clientes).

## 6. Obligaciones del Cliente (Responsable)

1. Base legal y avisos a titulares.  
2. Exactitud de datos cargados.  
3. No introducir datos ajenos al contrato.  
4. Designar contacto de privacidad.

## 7. Brechas

METGO notificará al contacto del Cliente según `RUNBOOK_BRECHAS_72H.md`. El Cliente decide notificación a Agencia/titulares cuando proceda.

## 8. Responsabilidad y ley

Ley chilena aplicable · Ley N° 21.719 y normas complementarias · Tribunales de `[comuna]`.

## Firmas

Cliente: _________________ fecha ____  
METGO: _________________ fecha ____

## Anexo A — Medidas (referencia repo)

- RAT: `RAT_METGO_v0.csv`  
- Olvido / portabilidad API  
- Backup: `RUNBOOK_BACKUP_RESTORE_R7.md`  
- Rotación: `ROTACION_SECRETS_R2.md`
