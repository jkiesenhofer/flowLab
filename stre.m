clear; clc;

% Parameter
rho_p = 2500;
rho_b = 1.293;
mu    = 1.8e-5;
Ub    = 5.0;
L     = 0.1;

i = 1:100;

dp = i * 1e-6;     % Partikeldurchmesser [m]
db = i * 1e-4;     % Blasendurchmesser [m]

% Kennzahlen
St  = rho_p .* dp.^2 .* Ub ./ (18 * mu * L); % Partikelträgheit zur Strömungsgeschwindigkeit des Fluids
Reb = Ub .* db .* rho_b ./ mu;               % Trägheitskräfte zu viskosen Kräfte

% Verhältnis
ratio = St ./ Reb;

% Plot
figure
plot(dp, ratio, 'LineWidth', 2)
grid on
xlabel('Partikeldurchmesser d_p [m]')
ylabel('St / Re_b [-]')
title('Verhältnis Stokeszahl zu Reynolds-Zahl')
