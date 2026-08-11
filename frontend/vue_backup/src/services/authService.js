/**
 * Servicio de autenticación METGO (Módulo 7 — capa sobre API JWT).
 * Centraliza mensajes de error y registro para las vistas Login/Registro.
 */
import { login as apiLogin, register as apiRegister } from '@/api/metgoApi'

export const AUTH_ERROR_INVALID = 'Usuario o contraseña incorrectos'

export async function login(username, password, sitio = 'quillota') {
  try {
    return await apiLogin(username, password, sitio)
  } catch (e) {
    const msg = e?.message || ''
    if (
      msg.includes('incorrectos') ||
      msg.includes('Credenciales') ||
      msg.includes('401')
    ) {
      throw new Error(AUTH_ERROR_INVALID)
    }
    throw e
  }
}

export async function register({ username, password, email, sitio = 'quillota' }) {
  return apiRegister({ username, password, email, sitio })
}
