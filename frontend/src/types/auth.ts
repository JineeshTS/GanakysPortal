/**
 * Authentication types
 */

export type UserRole = 'admin' | 'hr' | 'accountant' | 'employee';

export interface User {
  id: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  employee_id?: string;
  employee_name?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface TokenPayload {
  sub: string;
  email: string;
  role: UserRole;
  exp: number;
  iat: number;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  new_password: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
