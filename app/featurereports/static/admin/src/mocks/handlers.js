import { rest } from 'msw';

const mockData = {
  created_at: '2021-02-03T10:05:28.014020+00:00',
  updated_at: '2021-02-03T10:05:28.014034+00:00',
  custom_fields: [
    {
      title: 'TestField',
      name: 'testfield',
      type: 'string',
      required: true,
    },
    {
      title: 'TestField-TestTags',
      name: 'testfield_testtags',
      type: 'enum',
      required: true,
      enum: ['firstChoice','secondChoice'],
    },
  ],
  title: 'TestModel',
  name: 'testmodel',
  updated_by: 'testuserid',
  layer_id: 'TestLayer',
  created_by: 'testuserid',
  id: 'cc0e41cc-5e71-4ba8-b9ba-fc8606ac2105',
};

export const handlers = [
  rest.get('/report_models', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json([mockData]));
  }),

  rest.get('/report_models/1', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(mockData));
  }),

  rest.post('*', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(mockData));
  }),

  rest.put('*', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(mockData));
  }),

  rest.delete('*', (req, res, ctx) => {
    return res(ctx.status(204));
  }),
];
