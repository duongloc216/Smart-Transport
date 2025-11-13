import { useEffect } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet-routing-machine';
import 'leaflet-routing-machine/dist/leaflet-routing-machine.css';

/**
 * RoutingControl Component
 * Uses OSRM to draw real street-following routes
 */
const RoutingControl = ({ waypoints, color = '#4285F4' }) => {
  const map = useMap();

  useEffect(() => {
    if (!waypoints || waypoints.length < 2) return;

    // Create routing control
    const routingControl = L.Routing.control({
      waypoints: waypoints.map(wp => L.latLng(wp[0], wp[1])),
      routeWhileDragging: false,
      addWaypoints: false,
      draggableWaypoints: false,
      fitSelectedRoutes: false,
      showAlternatives: false,
      lineOptions: {
        styles: [
          {
            color: color,
            opacity: 0.8,
            weight: 6
          }
        ],
        extendToWaypoints: true,
        missingRouteTolerance: 0
      },
      router: L.Routing.osrmv1({
        serviceUrl: 'https://router.project-osrm.org/route/v1',
        profile: 'driving'
      }),
      createMarker: () => null, // Don't create default markers
      show: false, // Hide instructions panel
    }).addTo(map);

    // Hide the routing instructions container
    const container = routingControl.getContainer();
    if (container) {
      container.style.display = 'none';
    }

    return () => {
      if (map) {
        map.removeControl(routingControl);
      }
    };
  }, [map, waypoints, color]);

  return null;
};

export default RoutingControl;
