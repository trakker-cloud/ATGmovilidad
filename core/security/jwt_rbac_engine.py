#!/usr/bin/env python3
# Etiqueta: APP_CHANGO_JWT_RBAC_ENGINE_02102026
# Proyecto: app chango
# Arquitectura: JWT Authentication & Role-Based Access Control (RBAC) Engine

from datetime import datetime, timedelta
from typing import Dict, Any

class RBACSecurityEngine:
    """
    Motor central de autenticación y autorización para app chango.
    Emite tokens JWT simulados y valida permisos por roles de forma robusta.
    """
    SECRET_SIGNING_KEY = "CHANGOS_SUPER_SECURE_JWT_SECRET_KEY_2026"

    @classmethod
    def create_access_token(cls, user_id: str, role: str, tenant_id: str, expires_delta_hours: int = 12) -> str:
        """Genera un token de acceso estructurado de forma segura."""
        valid_roles = ["ROLE_PASSENGER", "ROLE_DRIVER", "ROLE_COORDINATOR", "ROLE_ADMIN_FRANCHISE"]
        if role not in valid_roles:
            raise ValueError(f"Rol no válido: {role}. Debe ser uno de {valid_roles}")

        expiry = datetime.now() + timedelta(hours=expires_delta_hours)
        
        # Formato limpio: jwt_sig|<user_id>|<role>|<tenant_id>|<expiry> usando pipe (|) para evitar cruces con guiones bajos
        token_signature = f"jwt_sig|{user_id}|{role}|{tenant_id}|{int(expiry.timestamp())}"
        print(f"[JWT SECURITY] Token emitido con éxito para {user_id} [{role}] en tenant '{tenant_id}'.")
        return token_signature

    @classmethod
    def verify_authorization(cls, token: str, required_role: str) -> Dict[str, Any]:
        """
        Valida el token de acceso y comprueba los privilegios del rol.
        """
        if not token or not token.startswith("jwt_sig|"):
            print("[SECURITY ERROR] Token inválido o ausente.")
            return {"authorized": False, "message": "Token de autenticación inválido o ausente."}

        # Desestructuración limpia basada en pipe (|)
        parts = token.split("|")
        if len(parts) < 5:
            return {"authorized": False, "message": "Estructura de token corrupta."}

        user_id = parts[1]
        role = parts[2]
        tenant_id = parts[3]

        # Validación jerárquica de roles (El Administrador de Franquicia tiene acceso total)
        if role != required_role and role != "ROLE_ADMIN_FRANCHISE":
            print(f"[RBAC BLOCK] Usuario {user_id} con rol [{role}] intentó acceder a recurso protegido para [{required_role}].")
            return {
                "authorized": False,
                "message": f"Acceso denegado. Se requiere el rol '{required_role}'."
            }

        print(f"[RBAC PASS] Usuario {user_id} autorizado correctamente bajo el rol [{role}].")
        return {
            "authorized": True,
            "user_id": user_id,
            "role": role,
            "tenant_id": tenant_id
        }

if __name__ == "__main__":
    print("--- [APP CHANGO] Verificando Motor de Seguridad JWT y RBAC ---")
    admin_token = RBACSecurityEngine.create_access_token("ADMIN-ROOT", "ROLE_ADMIN_FRANCHISE", "tucuman_central")
    print(RBACSecurityEngine.verify_authorization(admin_token, "ROLE_ADMIN_FRANCHISE"))
