import http from '../http-common';

class ReportModelApiService {
  getAll() {
    return http.get('');
  }

  get(id) {
    return http.get(`/${id}`);
  }

  create(data) {
    return http.post('', data);
  }

  update(id, data) {
    const { created_at, created_by, updated_at, updated_by, ...putData } = data;
    return http.put(`/${id}`, putData);
  }

  delete(id) {
    return http.delete(`/${id}`);
  }
}

export default new ReportModelApiService();
