program stokeszahl
  implicit none
  integer :: i
  real(8) :: dp, rho_p, mu, U1, U2, L, St1, St2

  rho_p = 2500.0d0      ! Partikeldichte [kg/m^3]
  mu    = 1.8d-5        ! dyn. Viskosität Luft [Pa s]
  U1    = 2.0d0         ! Strömungsgeschwindigkeit [m/s]
  U2    = 5.0d0         ! Strömungsgeschwindigkeit [m/s]
  L     = 0.1d0         ! charakteristische Länge [m]

  open(unit=10, file="stokes.dat", status="replace")

  do i = 1, 100
     dp = i * 1.0d-6    ! Partikeldurchmesser [m]
     St1 = rho_p * dp**2 * U1 / (18.0d0 * mu * L)
     St2 = rho_p * dp**2 * U2 / (18.0d0 * mu * L)
     write(10,*) dp, St2
  end do

  close(10)
end program stokeszahl
