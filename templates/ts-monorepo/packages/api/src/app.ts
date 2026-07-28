import express from 'express';
import cors from 'cors';

interface AppDeps {
  // Add your repository interfaces here.
  // Example: repository: MyRepository;
}

export function createApp(_deps: AppDeps): express.Application {
  const app = express();

  app.use(cors());
  app.use(express.json());

  app.get('/health', (_req, res) => {
    res.json({ status: 'healthy' });
  });

  // Mount your route handlers here.
  // Example: app.use('/api/v1/items', createItemsRouter(deps.repository));

  return app;
}
