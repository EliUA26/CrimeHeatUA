import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "./assets/vite.svg";
import heroImg from "./assets/hero.png";
import "./App.css";
import { useEffect } from "react";
import { useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet.heat";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

function HeatmapLayer() {
  const map = useMap();

  useEffect(() => {
    // 📍 Datos de ejemplo (puedes cambiar por Paraguay)
    const points = [
      [-25.28229, -57.63523, 1],
      [-25.282, -57.6355, 0.8],
      [-25.2818, -57.6351, 0.6],
      [-25.2825, -57.6349, 0.7],
      [-25.2827, -57.6356, 0.9],
      [-25.2819, -57.6347, 0.5],
    ];

    const heat = L.heatLayer(points, {
      radius: 10,
      blur: 8,
      maxZoom: 13,
      scaleRadius: false,
      max: 1.0,
      gradient: {
        0.2: "blue",
        0.4: "lime",
        0.6: "yellow",
        0.8: "orange",
        1.0: "red",
      },
    });

    heat.addTo(map);

    return () => {
      map.removeLayer(heat);
    };
  }, [map]);

  return null;
}

function App() {
  const position = [-25.282290696879606, -57.63523770675206];
  return (
    <>
      <section id="center">
        <MapContainer
          center={position}
          zoom={20}
          scrollWheelZoom={true}
          style={{ height: "600px", width: "100%" }}
        >
          <TileLayer url="https://mt0.google.com/vt/lyrs=m&x={x}&y={y}&z={z}" />
          <HeatmapLayer />
          <Marker position={position}>
            <Popup></Popup>
          </Marker>
        </MapContainer>
        <div className="panel">
          {/* aquí van tus filtros */}
          <h2>Filtros</h2>
        </div>
      </section>
    </>
  );
}

export default App;
