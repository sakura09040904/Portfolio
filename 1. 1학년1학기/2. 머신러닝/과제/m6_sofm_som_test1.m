clear;clf;
num_rows = 15;
num_cols = 15;
a = 0.20; % 이웃크기와 악습률의 감소를 위한 인자

% 초기 가중치 값 설정
% 주의: 이 예제는 2차원 데이터를 행렬이 아닌 복소수로 표현
dx = 0.1;
m = dx*(1-2*rand(num_rows,num_cols)) + dx*(1i-2i*rand(num_rows,num_cols));

for cycle = 1:5000

    eta = cycle^(-a);
    % 학습률 (얼마나 많은 노드를 움직일 것인가를 결정)
    G =0.5 + 10*cycle^(-a);% 가우시안 폭 관련 파라미터
     x = 1-2*rand;
     y = 1-2*rand;
     inp = x + y*1i; % 입력데이터 (복소수로 2차원 표현)

    
    % 승자 노드를 찾는다
    % 거리 행렬을 설정하고
    dist_mat = (real(m)-real(inp)).^2 + (imag(m)-imag(inp)).^2;
    % dist_mat를 벡터로 바꾸고, 최소 성분을 찾는다.
        [win_rows, win_cols] = find(dist_mat==min(dist_mat(:)));
            rand_idx = ceil(length(win_rows)*rand);
            % 이들 승자 중에서 임의의 하나를 선택한다.
        win_row = win_rows(rand_idx);
            win_col = win_cols(rand_idx);
            % 격자에서 승자로부터 거리를 계산하고
            [col_idx, row_idx] = meshgrid(1:num_cols, 1:num_rows);
            % 인덱스 행렬을 만들고
            grid_dist = abs(row_idx-win_row) + abs(col_idx-win_col);
            % 각 노드에 대하여 이웃의 크기를 나타내는 가우시안 커널을 계산한다.
            f = eta*exp(-(grid_dist/G).^2);

            % 특징 지도를 플롯
            if max(cycle == [1 10 30 50 100 200 400 600 800 1000 3000 5000])

               % 이 단계마다 플롯
               figure(1);
               if (cycle>1), delete(h); end % 이전 플롯은 지우고
               hold on;
               h = plot(real(m), imag(m), 'b-', real(m'), -imag(m'), 'k-');
               % 새로운 SOFM 격자를 그린다
               hold off;
               title(['훈련 횟수:' num2str(cycle) ...
                   ', 이웃의 크기' num2str(G) ...
                   ', 학습률:' num2str(eta)]);
               drawnow;

            end
                %%% 노드 이동
                m = m + f.*(inp-m);

end
