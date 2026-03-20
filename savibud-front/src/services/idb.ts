import { openDB } from 'idb';

const DB_NAME = 'offline-cache';

export async function saveDataToCache(data: unknown, store_name:string) {
  const db = await openDB(DB_NAME, 1, {
    upgrade(db) {
      db.createObjectStore(store_name);
    },
  });
  await db.put(store_name, data, 'all');
}

export async function getCachedData(store_name:string): Promise<unknown | null> {
  const db = await openDB(DB_NAME, 1);
  return db.get(store_name, 'all');
}
