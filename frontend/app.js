/* 3. Lógica y llamadas a la API (frontend/app.js) */


const { createApp, ref, onMounted } = Vue;

const API_BASE = "http://127.0.0.1:8000/api";

createApp({
  setup() {
    const tab = ref("trips");
    const authMode = ref("login");
    const token = ref(localStorage.getItem("token") || "");
    const loading = ref(false);

    const trips = ref([]);
    const matches = ref([]);
    const filterOrigin = ref("");
	
    // Formularios
    const loginForm = ref({ email: "", password: "" });

	const currentUser = ref(null);
	
	const passengerBookings = ref([]); // el pasajero ve sus reservas
    
	const regForm = ref({
      email: "",
      password: "",
      full_name: "",
      phone: "",
      favorite_team: "",
      is_driver: false,     // <-- Asegurar que exista
      is_passenger: true    // <-- Por defecto pasajero activado
    });
    const newTrip = ref({
      match_id: "",
      origin_city: "",
      meeting_point: "",
      departure_time: "",
      return_time: null,
      total_seats: 3,
      price_per_seat: 10,
      vehicle_info: "",
      notes: ""
    });

    const fetchTrips = async () => {
      loading.value = true;
      try {
        const url = filterOrigin.value 
          ? `${API_BASE}/trips/?origin=${encodeURIComponent(filterOrigin.value)}`
          : `${API_BASE}/trips/`;
        const res = await fetch(url);
        trips.value = await res.json();
      } catch (err) {
        console.error("Error al cargar viajes:", err);
      } finally {
        loading.value = false;
      }
    };

    const fetchMatches = async () => {
      try {
        const res = await fetch(`${API_BASE}/matches/`);
        matches.value = await res.json();
      } catch (err) {
        console.error("Error al cargar partidos:", err);
      }
    };

	const fetchMe = async () => {
		  if (!token.value) return;
		  try {
			const res = await fetch(`${API_BASE}/auth/me`, {
			  headers: { "Authorization": `Bearer ${token.value}` }
			});
			if (res.ok) {
			  currentUser.value = await res.json();
			} else {
			  // Si el token es inválido o caducó, limpiar sesión
			  logout();
			}
		  } catch (err) {
			console.error("Error al obtener perfil:", err);
		  }
	};




	const loginUser = async () => 
	{
      try {
        const body = new URLSearchParams();
        body.append("username", loginForm.value.email);
        body.append("password", loginForm.value.password);

        const res = await fetch(`${API_BASE}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: body.toString()
        });

        if (!res.ok) {
          const err = await res.json();
          return alert(err.detail || "Email o contraseña incorrectos");
        }

        const data = await res.json();
        token.value = data.access_token;
        localStorage.setItem("token", data.access_token);

        // Cargar inmediatamente el perfil del usuario
        await fetchMe();

        // Si existe la función para cargar solicitudes de conductor, llamarla
        if (typeof fetchDriverBookings === "function") {
          await fetchDriverBookings();
        }
		
		// El pasajero ve sus reservas
		if (typeof fetchPassengerBookings === "function") {
			await fetchPassengerBookings();
		}

        // Quedarse en la pestaña de cuenta para ver datos y roles
        tab.value = "auth";
        alert("¡Sesión iniciada con éxito!");
      } catch (e) {
        console.error(e);
        alert("No se pudo conectar con el servidor.");
      }
    };




    const registerUser = async () => {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(regForm.value)
      });

      if (!res.ok) {
        const err = await res.json();
        return alert(err.detail || "Error en el registro");
      }

      alert("Usuario registrado. Ya puedes iniciar sesión.");
      authMode.value = "login";
    };

    const submitTrip = async () => {
      // Ajustar fechas a formato ISO
      const payload = {
        ...newTrip.value,
        departure_time: new Date(newTrip.value.departure_time).toISOString(),
        return_time: newTrip.value.return_time ? new Date(newTrip.value.return_time).toISOString() : null
      };

      const res = await fetch(`${API_BASE}/trips/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token.value}`
        },
        body: JSON.stringify(payload)
      });

      if (!res.ok) return alert("Error al publicar el viaje");

      alert("¡Viaje publicado correctamente!");
      tab.value = "trips";
      fetchTrips();
    };

/* Añade la consulta de solicitudes y la acción para aceptarlas o rechazarlas:*/

	const driverBookings = ref([]);

    const fetchDriverBookings = async () => {
      if (!token.value) return;
      try {
        const res = await fetch(`${API_BASE}/trips/driver/bookings`, {
          headers: { "Authorization": `Bearer ${token.value}` }
        });
        if (res.ok) {
          driverBookings.value = await res.json();
        }
      } catch (err) {
        console.error("Error al cargar solicitudes:", err);
      }
    };

    const changeBookingStatus = async (bookingId, status) => {
      try {
        const res = await fetch(`${API_BASE}/trips/bookings/${bookingId}/status`, {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token.value}`
          },
          body: JSON.stringify({ status: status })
        });

        if (!res.ok) {
          const err = await res.json();
          return alert(err.detail || "No se pudo actualizar la reserva");
        }

        alert(status === 'accepted' ? "¡Plaza confirmada y restada del coche!" : "Solicitud rechazada");
        fetchDriverBookings();
        fetchTrips();
      } catch (e) {
        alert("Error de red al actualizar estado.");
      }
    };

/* FIN Añade la consulta de solicitudes y la acción para aceptarlas o rechazarlas:*/

    const reserveSeat = async (tripId) => {
      if (!token.value) {
        alert("Debes iniciar sesión para reservar una plaza.");
        tab.value = "auth";
        return;
      }

      const res = await fetch(`${API_BASE}/trips/book`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token.value}`
        },
        body: JSON.stringify({ trip_id: tripId, seats_requested: 1 })
      });

      if (!res.ok) {
        const err = await res.json();
        return alert(err.detail || "No se pudo solicitar la reserva");
      }

      alert("¡Solicitud enviada! El conductor la revisará.");
      fetchTrips();
    };

	// pasajero ve sus reservas
	const fetchPassengerBookings = async () => {
	  if (!token.value) return;
	  try {
		const res = await fetch(`${API_BASE}/trips/passenger/bookings`, {
		  headers: { "Authorization": `Bearer ${token.value}` }
		});
		if (res.ok) {
		  passengerBookings.value = await res.json();
		}
	  } catch (err) {
		console.error("Error al cargar reservas del pasajero:", err);
	  }
	};



    const logout = () => {
      token.value = "";
      localStorage.removeItem("token");
    };

    const formatDate = (dateStr) => {
      return new Date(dateStr).toLocaleString("es-ES", {
        weekday: "short",
        day: "numeric",
        month: "short",
        hour: "2-digit",
        minute: "2-digit"
      });
    };


    onMounted(() => {
      fetchTrips();
      fetchMatches();
	  if (token.value) {
        fetchMe();
        fetchDriverBookings(); // conductor ve sus reservas
		fetchPassengerBookings(); // pasajero ve sus reservas
      }
    });

    return {
      tab,
      authMode,
      token,
	  currentUser,
      trips,
      matches,
      filterOrigin,
      loading,
      loginForm,
      regForm,
      newTrip,
	  /* nuevas funciones */
	  driverBookings,
	  fetchDriverBookings,  
	  changeBookingStatus,
	  passengerBookings,
	  fetchPassengerBookings,
	  /* fin nuevas funciones */
      fetchTrips,
      loginUser,
      registerUser,
      submitTrip,
      reserveSeat,
      logout,
      formatDate
    };
  }
}).mount("#app");