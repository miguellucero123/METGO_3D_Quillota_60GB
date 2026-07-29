-- M7/M8: estaciones aire Escondida (FK aire_registros → estaciones).

insert into public.estaciones (id, nombre, sitio, lat, lon) values
  ('escondida', 'Escondida', 'spati', -24.251667, -69.054167),
  ('escondida_rajo', 'Escondida rajo', 'spati', -24.251667, -69.054167)
on conflict (id) do update set
  nombre = excluded.nombre,
  sitio = excluded.sitio,
  lat = excluded.lat,
  lon = excluded.lon;
