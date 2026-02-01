% Parameter
rho = 1000;        % Dichte [kg/m^3]
sigma = 0.072;     % Oberflächenspannung [N/m]
d = 1e-3;          % charakteristische Länge [m]

% Energiedissipationsrate
epsilon = logspace(-3, 2, 100); % [m^2/s^3]

% Weber-Zahl
We = (rho/sigma) .* epsilon.^(2/3) .* d.^(5/3);

% Plot
figure
loglog(epsilon, We, 'LineWidth', 2)
grid on
xlabel('\epsilon  [m^2/s^3]')
ylabel('Weber number')
