/**
 * Employees API
 */

import api from './client';
import type {
  Employee,
  EmployeeContact,
  EmployeeIdentity,
  EmployeeBank,
  EmployeeEmployment,
  EmployeeDocument,
  EmployeeCreateRequest,
  EmployeeListParams,
  Department,
  Designation,
} from '@/types/employee';

interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export const employeesApi = {
  // Employees
  getEmployees: async (params?: EmployeeListParams): Promise<PaginatedResponse<Employee>> => {
    const searchParams: Record<string, string> = {};
    if (params?.search) searchParams.search = params.search;
    if (params?.department_id) searchParams.department_id = params.department_id;
    if (params?.designation_id) searchParams.designation_id = params.designation_id;
    if (params?.status) searchParams.status = params.status;
    if (params?.skip !== undefined) searchParams.skip = String(params.skip);
    if (params?.limit !== undefined) searchParams.limit = String(params.limit);

    return api.get<PaginatedResponse<Employee>>('/employees', { params: searchParams });
  },

  getEmployee: async (id: string): Promise<Employee> => {
    return api.get<Employee>(`/employees/${id}`);
  },

  createEmployee: async (data: EmployeeCreateRequest): Promise<Employee> => {
    return api.post<Employee>('/employees', data);
  },

  updateEmployee: async (id: string, data: Partial<Employee>): Promise<Employee> => {
    return api.patch<Employee>(`/employees/${id}`, data);
  },

  // Contact
  updateContact: async (id: string, data: Partial<EmployeeContact>): Promise<EmployeeContact> => {
    return api.put<EmployeeContact>(`/employees/${id}/contact`, data);
  },

  // Identity
  updateIdentity: async (id: string, data: Partial<EmployeeIdentity>): Promise<EmployeeIdentity> => {
    return api.put<EmployeeIdentity>(`/employees/${id}/identity`, data);
  },

  // Bank
  updateBank: async (id: string, data: Partial<EmployeeBank>): Promise<EmployeeBank> => {
    return api.put<EmployeeBank>(`/employees/${id}/bank`, data);
  },

  // Employment
  updateEmployment: async (
    id: string,
    data: Partial<EmployeeEmployment>
  ): Promise<EmployeeEmployment> => {
    return api.put<EmployeeEmployment>(`/employees/${id}/employment`, data);
  },

  // Documents
  getDocuments: async (employeeId: string): Promise<EmployeeDocument[]> => {
    return api.get<EmployeeDocument[]>(`/employees/${employeeId}/documents`);
  },

  uploadDocument: async (
    employeeId: string,
    documentType: string,
    file: File,
    description?: string
  ): Promise<EmployeeDocument> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);
    if (description) formData.append('description', description);

    return api.uploadFormData<EmployeeDocument>(
      `/employees/${employeeId}/documents`,
      formData
    );
  },

  deleteDocument: async (employeeId: string, documentId: string): Promise<void> => {
    await api.delete(`/employees/${employeeId}/documents/${documentId}`);
  },

  verifyDocument: async (employeeId: string, documentId: string): Promise<EmployeeDocument> => {
    return api.patch<EmployeeDocument>(
      `/employees/${employeeId}/documents/${documentId}/verify`,
      {}
    );
  },

  // Departments
  getDepartments: async (): Promise<Department[]> => {
    return api.get<Department[]>('/departments');
  },

  // Designations
  getDesignations: async (departmentId?: string): Promise<Designation[]> => {
    const params = departmentId ? { department_id: departmentId } : undefined;
    return api.get<Designation[]>('/designations', { params });
  },
};

export default employeesApi;
