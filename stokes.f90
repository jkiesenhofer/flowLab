program stokeszahl
  implicit none
  integer :: i
  real(8) :: dp, rho_p, mu, Ua, Ub, Uc, L, K1, K2, K3

  rho_p = 2500.0d0      ! Partikeldichte [kg/m^3]
  mu    = 1.8d-5        ! dyn. Viskosität Luft [Pa s]
  Ua    = 2.0d0         ! Strömungsgeschwindigkeit [m/s]
  Ub    = 5.0d0         ! Strömungsgeschwindigkeit [m/s]
  Uc    = 8.0d0         ! Strömungsgeschwindigkeit [m/s]
  L     = 0.1d0         ! charakteristische Länge [m]

  open(unit=10, file="stokes.dat", status="replace")

  do i = 1, 100
     dp = i * 1.0d-6    ! Partikeldurchmesser [m]
     K1 = rho_p * dp**2 * Ua / (18.0d0 * mu * L)
     K2 = rho_p * dp**2 * Ub / (18.0d0 * mu * L)
     K3 = rho_p * dp**2 * Uc / (18.0d0 * mu * L)
     write(10,*) dp, K1, K2, K3
  end do

  close(10)
end program stokeszahl
