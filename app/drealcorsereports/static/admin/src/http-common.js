import axios from 'axios';

export default axios.create({
  baseURL: '../report_models',
  headers: {
    'Content-type': 'application/json',
  },
});

export function getErrorMessage(error) {
  let errorMessage;
  if (error.response === undefined) {
    errorMessage = 'Veuillez vérifier votre connexion internet';
  } else if (error.response.status === 400 && error.response.data.errors) {
    errorMessage = error.response.data.errors[0].description[0];
  } else {
    errorMessage = error.response.data;
  }
  return errorMessage;
}
