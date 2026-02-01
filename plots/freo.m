g = 9.81;          % Erdbeschleunigung [m/s^2]
rho_diff = 7900;   % Dichteunterschied [kg/m^3]
sigma = 0.072;     % Oberflächenspannung Wasser/Luft [N/m]
v = 5;             % charakteristische Geschwindigkeit [m/s]

L = logspace(-4, 0, 200);  % Länge von 0.1 mm bis 1 m


Fr = v ./ sqrt(g .* L);
Eo = (rho_diff .* g .* L.^2) ./ sigma;


figure
loglog(Eo, Fr, 'LineWidth', 2)
legend('Fr(Eo)')
grid on
xlabel('Eötvös-Zahl (Eo)')
ylabel('Froude-Zahl (Fr)')
