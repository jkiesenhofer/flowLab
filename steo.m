% Konstanten
rho_l = 1000;      % Dichte Flüssigkeit [kg/m^3]
rho_g = 1.2;       % Dichte Gas [kg/m^3]
rho_p = 7900;      % Partikeldichte [kg/m^3]
g = 9.81;          % Erdbeschleunigung [m/s^2]
sigma = 0.072;     % Oberflächenspannung [N/m]
mu = 1e-3;         % dynamische Viskosität [Pa s]
tau_f = 0.01;      % charakteristische Strömungszeit [s]

% Partikeldurchmesser
d = linspace(1e-5, 2e-3, 200);  % [m]
v = randi(500,1,200);
% Eötvöszahl
Eo = (rho_l - rho_g) .* g .* d.^2 ./ sigma; % Gravitationskräfte zu Oberflächenspannungskräfte

% Stokeszahl
tau_p = rho_p .* d.^2 ./ (18 * mu);
St = tau_p ./ tau_f     % Partikelträgheit zur Strömungsgeschwindigkeit des Fluids

% Plot
figure
loglog(St, Eo, 'LineWidth', 2)
xlabel('Stokeszahl St')
ylabel('Eötvöszahl Eo')
grid on
