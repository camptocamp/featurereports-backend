import axios from 'axios';

export default axios.create({
  baseURL: '/report_models',
  headers: {
    'Content-type': 'application/json',
  },
});
