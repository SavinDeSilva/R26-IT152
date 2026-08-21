import { MapContainer, TileLayer, Marker, Popup, CircleMarker, useMap } from 'react-leaflet'
import L from 'leaflet'
import { useEffect } from 'react'
import { T } from '../theme'

const touristIcon = new L.Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

function Recenter({ lat, lng }) {
  const map = useMap()
  useEffect(() => {
    if (lat != null && lng != null) map.setView([lat, lng], map.getZoom(), { animate: true })
  }, [lat, lng, map])
  return null
}

export default function LiveMap({ latitude, longitude, stationLat, stationLng, height = 400 }) {
  const lat = latitude ?? 6.9271
  const lng = longitude ?? 79.8612

  return (
    <div
      style={{
        width: '100%',
        height,
        borderRadius: 12,
        overflow: 'hidden',
        border: `1px solid ${T.line}`,
        background: T.lineSoft,
        boxShadow: T.shadowSm,
      }}
    >
      <MapContainer center={[lat, lng]} zoom={14} style={{ height: '100%', width: '100%' }}>
        <TileLayer attribution='&copy; OSM' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <Recenter lat={lat} lng={lng} />
        <Marker position={[lat, lng]} icon={touristIcon}>
          <Popup>Tourist live position</Popup>
        </Marker>
        {stationLat != null && stationLng != null && (
          <CircleMarker
            center={[stationLat, stationLng]}
            radius={9}
            pathOptions={{ color: T.ocean, fillColor: T.emerald, fillOpacity: 0.85 }}
          >
            <Popup>Assigned station</Popup>
          </CircleMarker>
        )}
      </MapContainer>
    </div>
  )
}
