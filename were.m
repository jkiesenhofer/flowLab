% Parameter
rho = 7900;        % Dichte [kg/m^3]
mu = 1e-3;         % dyn. Viskosität [Pa s]
sigma = 0.072;     % Oberflächenspannung [N/m]
L = 1e-3;          % charakteristische Länge [m]


% Geschwindigkeit
v = linspace(0.01, 5, 100);

% Reynolds- und Weber-Zahl
Re = rho .* v .* L ./ mu;       % Trägheitskräfte zu viskosen Kräfte
We = rho .* v.^2 .* L ./ sigma; % Trägheitskräfte zu Oberflächenspannungskräfte

% Plot
figure
loglog(Re, We, 'LineWidth', 2)
xlabel('Reynolds-Zahl')
ylabel('Weber-Zahl')
grid on
