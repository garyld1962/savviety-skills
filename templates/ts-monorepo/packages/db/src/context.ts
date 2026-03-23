import { createClient } from '@libsql/client';
import { drizzle } from 'drizzle-orm/libsql';
import { sql } from 'drizzle-orm';
import * as schema from './schema';

export interface DatabaseConfig {
  url: string;
}

export interface DatabaseContext {
  db: ReturnType<typeof drizzle>;
  close: () => void;
}

export function createDatabaseContext(config: DatabaseConfig): DatabaseContext {
  const client = createClient({ url: config.url });
  const db = drizzle(client, { schema });

  return {
    db,
    close: () => {
      client.close();
    },
  };
}
