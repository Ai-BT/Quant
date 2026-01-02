<template>
  <div class="container">
    <!-- Header -->
    <div class="header">
      <h1>📈 Quant Trading System</h1>
      <p>24시간 무중단 자동 트레이딩 시스템</p>
    </div>

    <!-- Server Status -->
    <div class="status-grid">
      <div class="status-card">
        <h3>서버 상태</h3>
        <div class="value" :class="`status-${healthStatus}`">
          {{ healthStatusText }}
        </div>
        <div v-if="healthData" style="margin-top: 10px; font-size: 0.85rem; color: #666;">
          업타임: {{ formatUptime(healthData.uptime_seconds) }}
        </div>
      </div>
      <div class="status-card">
        <h3>실행 중인 전략</h3>
        <div class="value">{{ runningStrategiesCount }}</div>
      </div>
      <div class="status-card">
        <h3>총 포지션</h3>
        <div class="value">{{ positions.length }}</div>
        <div v-if="totalBalance > 0" style="margin-top: 5px; font-size: 0.85rem; color: #666;">
          총 평가액: {{ formatPrice(totalBalance) }}원
        </div>
      </div>
      <div class="status-card">
        <h3>최근 거래</h3>
        <div class="value">{{ trades.length }}</div>
      </div>
    </div>

    <!-- Virtual Account Section -->
    <div class="section">
      <h2>가상 계좌 (시뮬레이션)</h2>
      <div v-if="virtualAccount">
        <div class="account-summary">
          <div class="account-item">
            <span class="account-label">초기 자본:</span>
            <span class="account-value">{{ formatPrice(virtualAccount.summary?.initial_balance || 0) }}원</span>
          </div>
          <div class="account-item">
            <span class="account-label">현재 잔고:</span>
            <span class="account-value">{{ formatPrice(virtualAccount.balance || 0) }}원</span>
          </div>
          <div class="account-item">
            <span class="account-label">총 자산:</span>
            <span class="account-value highlight">{{ formatPrice(virtualAccount.total_value || 0) }}원</span>
          </div>
          <div class="account-item">
            <span class="account-label">손익:</span>
            <span class="account-value" :class="(virtualAccount.summary?.profit_loss || 0) >= 0 ? 'text-green' : 'text-red'">
              {{ formatPrice(virtualAccount.summary?.profit_loss || 0) }}원
              ({{ (virtualAccount.summary?.profit_loss_rate || 0).toFixed(2) }}%)
            </span>
          </div>
        </div>
        <div v-if="virtualAccount.holdings && Object.keys(virtualAccount.holdings).length > 0" style="margin-top: 20px;">
          <h3 style="margin-bottom: 10px;">보유 코인 (전체 합계)</h3>
          <table class="table">
            <thead>
              <tr>
                <th>코인</th>
                <th>보유량</th>
                <th>평균 매수가</th>
                <th>현재가</th>
                <th>평가금액</th>
                <th>손익</th>
                <th>손익률</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(quantity, currency) in virtualAccount.holdings" :key="currency">
                <td><strong>{{ currency }}</strong></td>
                <td>{{ formatNumber(quantity) }}</td>
                <td>{{ formatPrice(virtualAccount.avg_buy_prices?.[currency] || 0) }}원</td>
                <td>{{ formatPrice(virtualAccount.prices?.[currency] || 0) }}원</td>
                <td>{{ formatPrice((virtualAccount.prices?.[currency] || 0) * quantity) }}원</td>
                <td :class="getVirtualAccountProfitLoss(currency, quantity) >= 0 ? 'text-green' : 'text-red'">
                  {{ formatPrice(getVirtualAccountProfitLoss(currency, quantity)) }}원
                </td>
                <td :class="getVirtualAccountProfitLossRate(currency, quantity) >= 0 ? 'text-green' : 'text-red'">
                  {{ getVirtualAccountProfitLossRate(currency, quantity) >= 0 ? '+' : '' }}{{ getVirtualAccountProfitLossRate(currency, quantity).toFixed(2) }}%
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div v-else style="text-align: center; padding: 40px; color: #666;">
        가상 계좌 정보를 불러오는 중...
      </div>
    </div>

    <!-- Strategy Accounts Section -->
    <div class="section" v-if="strategyAccounts.length > 0">
      <h2>전략별 가상 계좌 (전략당 500만원 할당)</h2>
      <div v-for="strategyAccount in strategyAccounts" :key="strategyAccount.strategy_id" style="margin-bottom: 30px; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
        <h3 style="margin-bottom: 15px;">{{ strategyAccount.strategy_id }}</h3>
        <div class="account-summary">
          <div class="account-item">
            <span class="account-label">초기 자본:</span>
            <span class="account-value">{{ formatPrice(strategyAccount.summary?.initial_balance || 0) }}원</span>
          </div>
          <div class="account-item">
            <span class="account-label">현재 잔고:</span>
            <span class="account-value">{{ formatPrice(strategyAccount.balance || 0) }}원</span>
          </div>
          <div class="account-item">
            <span class="account-label">총 자산:</span>
            <span class="account-value highlight">{{ formatPrice(strategyAccount.total_value || 0) }}원</span>
          </div>
          <div class="account-item">
            <span class="account-label">손익:</span>
            <span class="account-value" :class="(strategyAccount.summary?.profit_loss || 0) >= 0 ? 'text-green' : 'text-red'">
              {{ formatPrice(strategyAccount.summary?.profit_loss || 0) }}원
              ({{ (strategyAccount.summary?.profit_loss_rate || 0).toFixed(2) }}%)
            </span>
          </div>
          <div class="account-item">
            <span class="account-label">거래 횟수:</span>
            <span class="account-value">{{ strategyAccount.trade_count || 0 }}회</span>
          </div>
        </div>
        <div v-if="strategyAccount.holdings && Object.keys(strategyAccount.holdings).length > 0" style="margin-top: 15px;">
          <h4 style="margin-bottom: 10px; font-size: 0.95rem;">보유 코인</h4>
          <table class="table">
            <thead>
              <tr>
                <th>코인</th>
                <th>보유량</th>
                <th>평균 매수가</th>
                <th>현재가</th>
                <th>평가금액</th>
                <th>손익</th>
                <th>손익률</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(quantity, currency) in strategyAccount.holdings" :key="currency">
                <td><strong>{{ currency }}</strong></td>
                <td>{{ formatNumber(quantity) }}</td>
                <td>{{ formatPrice(strategyAccount.avg_buy_prices?.[currency] || 0) }}원</td>
                <td>{{ formatPrice((strategyAccount.prices?.[currency] || strategyAccount.summary?.prices?.[currency] || 0)) }}원</td>
                <td>{{ formatPrice((strategyAccount.prices?.[currency] || strategyAccount.summary?.prices?.[currency] || 0) * quantity) }}원</td>
                <td :class="getStrategyAccountProfitLoss(strategyAccount, currency, quantity) >= 0 ? 'text-green' : 'text-red'">
                  {{ formatPrice(getStrategyAccountProfitLoss(strategyAccount, currency, quantity)) }}원
                </td>
                <td :class="getStrategyAccountProfitLossRate(strategyAccount, currency, quantity) >= 0 ? 'text-green' : 'text-red'">
                  {{ getStrategyAccountProfitLossRate(strategyAccount, currency, quantity) >= 0 ? '+' : '' }}{{ getStrategyAccountProfitLossRate(strategyAccount, currency, quantity).toFixed(2) }}%
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Account Info Section -->
    <div class="section">
      <h2>실제 계좌 정보</h2>
      <div v-if="accountsError" class="error">{{ accountsError }}</div>
      <div>
        <div class="account-summary">
          <div class="account-item">
            <span class="account-label">KRW 잔고:</span>
            <span class="account-value">{{ formatPrice(krwBalance) }}원</span>
          </div>
          <div class="account-item">
            <span class="account-label">총 보유 코인:</span>
            <span class="account-value">{{ accounts.length }}개</span>
          </div>
          <div class="account-item">
            <span class="account-label">총 평가액:</span>
            <span class="account-value highlight">{{ formatPrice(totalBalance + krwBalance) }}원</span>
          </div>
        </div>
        <table class="table" style="margin-top: 20px;">
          <thead>
            <tr>
              <th>화폐</th>
              <th>보유량</th>
              <th>평균 매수가</th>
              <th>현재가</th>
              <th>평가금액</th>
              <th>손익</th>
              <th>손익률</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="account in accounts" :key="account.currency">
              <td><strong>{{ account.currency }}</strong></td>
              <td>{{ formatNumber(parseFloat(account.balance)) }}</td>
              <td v-if="account.currency === 'KRW'">-</td>
              <td v-else>{{ formatPrice(parseFloat(account.avg_buy_price || 0)) }}원</td>
              <td v-if="account.currency === 'KRW'">-</td>
              <td v-else>{{ formatPrice(accountCurrentPrice(account.currency)) }}원</td>
              <td v-if="account.currency === 'KRW'">{{ formatPrice(parseFloat(account.balance)) }}원</td>
              <td v-else>{{ formatPrice(accountCurrentPrice(account.currency) * parseFloat(account.balance)) }}원</td>
              <td v-if="account.currency === 'KRW'">-</td>
              <td v-else :class="getAccountProfitLoss(account) >= 0 ? 'text-green' : 'text-red'">
                {{ formatPrice(getAccountProfitLoss(account)) }}원
              </td>
              <td v-if="account.currency === 'KRW'">-</td>
              <td v-else :class="getAccountProfitLossRate(account) >= 0 ? 'text-green' : 'text-red'">
                {{ getAccountProfitLossRate(account) >= 0 ? '+' : '' }}{{ getAccountProfitLossRate(account).toFixed(2) }}%
              </td>
            </tr>
            <tr v-if="accounts.length === 0">
              <td colspan="7" style="text-align: center; padding: 40px; color: #666;">
                계좌 정보가 없습니다.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Strategies Section -->
    <div class="section">
      <h2>전략 관리</h2>
      <div v-if="strategiesError" class="error">{{ strategiesError }}</div>
      <div class="strategy-list">
        <div v-for="strategy in strategies" :key="strategy.id" class="strategy-item">
          <div class="strategy-info">
            <div class="strategy-name">{{ strategy.name }}</div>
            <div class="strategy-meta">
              {{ strategy.type }} • {{ strategy.market }}
            </div>
          </div>
          <div style="display: flex; align-items: center;">
            <span 
              class="strategy-status" 
              :class="strategy.status"
            >
              {{ strategy.status === 'running' ? '실행 중' : '중지됨' }}
            </span>
            <button
              v-if="strategy.status === 'stopped'"
              class="btn btn-success"
              @click="handleStartStrategy(strategy.id)"
              :disabled="loading"
            >
              시작
            </button>
            <button
              v-else
              class="btn btn-danger"
              @click="handleStopStrategy(strategy.id)"
              :disabled="loading"
            >
              중지
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Positions Section -->
    <div class="section" style="position: relative;">
      <h2>현재 포지션</h2>
      <div v-if="positionsError" class="error">{{ positionsError }}</div>
      <div>
        <table class="table">
          <thead>
            <tr>
              <th>마켓</th>
              <th>보유량</th>
              <th>평균 매수가</th>
              <th>현재가</th>
              <th>평가금액</th>
              <th>손익</th>
              <th>손익률</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="position in positions" :key="position.market">
              <td><strong>{{ position.market }}</strong></td>
              <td>{{ formatNumber(position.balance) }} {{ position.currency }}</td>
              <td>{{ formatPrice(position.avg_buy_price) }}원</td>
              <td>{{ formatPrice(position.current_price) }}원</td>
              <td>{{ formatPrice(position.total_value || (position.current_price * position.balance)) }}원</td>
              <td :class="position.profit_loss >= 0 ? 'text-green' : 'text-red'">
                {{ formatPrice(position.profit_loss) }}원
              </td>
              <td :class="position.profit_loss_rate >= 0 ? 'text-green' : 'text-red'">
                {{ position.profit_loss_rate >= 0 ? '+' : '' }}{{ position.profit_loss_rate.toFixed(2) }}%
              </td>
            </tr>
            <tr v-if="positions.length === 0">
              <td colspan="7" style="text-align: center; padding: 40px; color: #666;">
                포지션이 없습니다.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Virtual Trades Section -->
    <div class="section">
      <h2>가상 계좌 거래 내역</h2>
      <div>
        <table class="table">
          <thead>
            <tr>
              <th>날짜</th>
              <th>구분</th>
              <th>코인</th>
              <th>가격</th>
              <th>수량</th>
              <th>금액</th>
              <th>수수료</th>
              <th>잔고</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="trade in virtualTrades" :key="trade.timestamp">
              <td>{{ formatDateTime(trade.timestamp) }}</td>
              <td>
                <span class="badge" :class="trade.type === 'BUY' ? 'badge-success' : 'badge-danger'">
                  {{ trade.type === 'BUY' ? '매수' : '매도' }}
                </span>
              </td>
              <td><strong>{{ trade.currency }}</strong></td>
              <td>{{ formatPrice(trade.price) }}원</td>
              <td>{{ formatNumber(trade.quantity) }}</td>
              <td>{{ formatPrice(trade.amount) }}원</td>
              <td>{{ formatPrice(trade.commission) }}원</td>
              <td>{{ formatPrice(trade.balance_after) }}원</td>
            </tr>
            <tr v-if="virtualTrades.length === 0">
              <td colspan="8" style="text-align: center; padding: 40px; color: #666;">
                거래 내역이 없습니다.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Trades Section -->
    <div class="section">
      <h2>실제 계좌 거래 내역</h2>
      <div v-if="tradesError" class="error">{{ tradesError }}</div>
      <div>
        <table class="table">
          <thead>
            <tr>
              <th>시간</th>
              <th>마켓</th>
              <th>종류</th>
              <th>가격</th>
              <th>수량</th>
              <th>금액</th>
              <th>수수료</th>
              <th>상태</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="trade in trades" :key="trade.id">
              <td>{{ formatDateTime(trade.created_at) }}</td>
              <td><strong>{{ trade.market }}</strong></td>
              <td>
                <span class="badge" :class="trade.side === 'bid' ? 'badge-success' : 'badge-danger'">
                  {{ trade.side === 'bid' ? '매수' : '매도' }}
                </span>
              </td>
              <td>{{ formatPrice(trade.price) }}원</td>
              <td>{{ formatNumber(trade.volume) }}</td>
              <td>{{ formatPrice(trade.amount) }}원</td>
              <td>{{ formatPrice(trade.fee) }}원</td>
              <td>
                <span class="badge badge-info">{{ trade.status }}</span>
              </td>
            </tr>
            <tr v-if="trades.length === 0">
              <td colspan="8" style="text-align: center; padding: 40px; color: #666;">
                거래 내역이 없습니다.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Refresh Button -->
    <button class="refresh-btn" @click="refreshAll" :disabled="loading">
      🔄
    </button>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { healthApi, strategyApi, positionApi, tradeApi, upbitApi, virtualAccountApi } from './api'

export default {
  name: 'App',
  setup() {
    // State
    const healthData = ref(null)
    const healthStatus = ref('healthy')
    const strategies = ref([])
    const positions = ref([])
    const trades = ref([])
    const accounts = ref([])
    const accountPrices = ref({}) // 화폐별 현재가 저장
    const virtualAccount = ref(null)
    const virtualTrades = ref([])
    const strategyAccounts = ref([])  // 전략별 계좌 목록
    const loading = ref(false)
    const loadingStrategies = ref(false)
    const loadingPositions = ref(false)
    const loadingTrades = ref(false)
    const loadingAccounts = ref(false)
    const strategiesError = ref(null)
    const positionsError = ref(null)
    const tradesError = ref(null)
    const accountsError = ref(null)

    // Computed
    const runningStrategiesCount = computed(() => {
      return strategies.value.filter(s => s.status === 'running').length
    })

    const totalBalance = computed(() => {
      return positions.value.reduce((sum, pos) => {
        return sum + (pos.current_price * pos.balance)
      }, 0)
    })

    const krwBalance = computed(() => {
      const krwAccount = accounts.value.find(acc => acc.currency === 'KRW')
      return krwAccount ? parseFloat(krwAccount.balance) : 0
    })

    const healthStatusText = computed(() => {
      const statusMap = {
        healthy: '정상',
        degraded: '주의',
        unhealthy: '오류'
      }
      return statusMap[healthStatus.value] || '확인 중'
    })

    // Methods
    const formatUptime = (seconds) => {
      const days = Math.floor(seconds / 86400)
      const hours = Math.floor((seconds % 86400) / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      
      if (days > 0) return `${days}일 ${hours}시간`
      if (hours > 0) return `${hours}시간 ${minutes}분`
      return `${minutes}분`
    }

    const formatPrice = (price) => {
      return new Intl.NumberFormat('ko-KR').format(Math.round(price))
    }

    const formatNumber = (num) => {
      return new Intl.NumberFormat('ko-KR', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 8,
      }).format(num)
    }

    const formatDateTime = (dateString) => {
      const date = new Date(dateString)
      return new Intl.DateTimeFormat('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      }).format(date)
    }

    const fetchHealth = async () => {
      try {
        const response = await healthApi.getHealth()
        healthData.value = response.data
        healthStatus.value = response.data.status || 'healthy'
      } catch (error) {
        console.error('Health check failed:', error)
        healthStatus.value = 'unhealthy'
      }
    }

    const fetchAccounts = async (showLoading = true) => {
      if (showLoading) loadingAccounts.value = true
      accountsError.value = null
      try {
        // 실제 Upbit 계좌 정보 가져오기
        const accountsResponse = await upbitApi.getAccounts()
        console.log('계좌 응답 전체:', accountsResponse)
        console.log('계좌 응답 data:', accountsResponse.data)
        const allAccounts = accountsResponse.data?.data || accountsResponse.data || []
        console.log('전체 계좌:', allAccounts)
        console.log('계좌 개수:', allAccounts.length)
        
        // 보유 코인의 현재가 정보 가져오기 (KRW 제외, 잔고 > 0)
        const coinAccounts = allAccounts.filter(acc => acc.currency !== 'KRW' && parseFloat(acc.balance) > 0)
        console.log('보유 코인:', coinAccounts)
        
        if (coinAccounts.length > 0) {
          const markets = coinAccounts.map(acc => `KRW-${acc.currency}`).join(',')
          console.log('요청 마켓:', markets)
          try {
            const tickerResponse = await upbitApi.getTicker(markets)
            console.log('티커 응답 전체:', tickerResponse)
            console.log('티커 응답 data:', tickerResponse.data)
            console.log('티커 응답 data.data:', tickerResponse.data?.data)
            console.log('티커 응답 data.data 타입:', typeof tickerResponse.data?.data)
            const tickers = tickerResponse.data?.data || tickerResponse.data || []
            console.log('티커 데이터:', tickers)
            console.log('티커 데이터 길이:', tickers.length)
            
            // 티커를 화폐 코드로 매핑
            if (Array.isArray(tickers) && tickers.length > 0) {
              console.log('티커 개수:', tickers.length)
              tickers.forEach(ticker => {
                if (ticker && ticker.market) {
                  const currency = ticker.market.replace('KRW-', '')
                  if (ticker.trade_price) {
                    accountPrices.value[currency] = ticker.trade_price
                    console.log(`가격 매핑: ${currency} = ${ticker.trade_price}`)
                  } else {
                    console.log(`가격 없음: ${currency}`, ticker)
                  }
                } else {
                  console.log('유효하지 않은 티커:', ticker)
                }
              })
              console.log('매핑된 가격 전체:', accountPrices.value)
            } else {
              console.warn('티커 데이터가 배열이 아니거나 비어있음:', tickers)
            }
          } catch (error) {
            console.error('현재가 조회 실패:', error)
            // 에러 무시 (일부 마켓이 존재하지 않을 수 있음)
          }
          
          // 상장폐지된 코인 및 1만원 이하 필터링
          // KRW는 항상 표시, 코인은 Ticker 데이터가 있고 평가액이 1만원 초과인 것만 표시
          accounts.value = allAccounts.filter(acc => {
            if (acc.currency === 'KRW') return true // KRW는 항상 표시
            const balance = parseFloat(acc.balance)
            if (balance === 0) return false
            const currentPrice = accountPrices.value[acc.currency]
            // 현재가가 없거나 0이면 필터링에서 제외 (상장폐지된 마켓)
            if (!currentPrice || currentPrice === 0) {
              console.log(`필터링 제외: ${acc.currency} (상장폐지 또는 존재하지 않는 마켓)`)
              return false
            }
            // 평가액 계산
            const totalValue = currentPrice * balance
            // 1만원 이하는 제외
            if (totalValue <= 10000) {
              console.log(`필터링 제외: ${acc.currency} (평가액 ${totalValue.toLocaleString()}원 ≤ 1만원)`)
              return false
            }
            console.log(`✅ 표시: ${acc.currency} (평가액 ${totalValue.toLocaleString()}원)`)
            return true
          })
          
          // 평가액 순서대로 정렬 (내림차순)
          accounts.value.sort((a, b) => {
            if (a.currency === 'KRW') return -1 // KRW는 맨 위
            if (b.currency === 'KRW') return 1
            const aPrice = accountPrices.value[a.currency] || 0
            const bPrice = accountPrices.value[b.currency] || 0
            const aValue = aPrice * parseFloat(a.balance)
            const bValue = bPrice * parseFloat(b.balance)
            return bValue - aValue // 내림차순
          })
          
          console.log('필터링 및 정렬 후 계좌:', accounts.value)
        } else {
          // 코인이 없으면 KRW만 표시
          accounts.value = allAccounts.filter(acc => acc.currency === 'KRW')
          console.log('KRW만 표시:', accounts.value)
        }
      } catch (error) {
        console.error('Failed to fetch accounts:', error)
        accountsError.value = '계좌 정보를 불러오는데 실패했습니다.'
        accounts.value = []
      } finally {
        if (showLoading) loadingAccounts.value = false
      }
    }

    const fetchStrategies = async (showLoading = true) => {
      if (showLoading) loadingStrategies.value = true
      strategiesError.value = null
      try {
        const response = await strategyApi.getStrategies()
        strategies.value = response.data
      } catch (error) {
        console.error('Failed to fetch strategies:', error)
        strategiesError.value = '전략 목록을 불러오는데 실패했습니다.'
      } finally {
        if (showLoading) loadingStrategies.value = false
      }
    }

    const fetchPositions = async (showLoading = true) => {
      if (showLoading) loadingPositions.value = true
      positionsError.value = null
      try {
        // 실제 Upbit 계좌 정보 가져오기
        const accountsResponse = await upbitApi.getAccounts()
        console.log('포지션 - 계좌 응답:', accountsResponse)
        const accounts = accountsResponse.data?.data || accountsResponse.data || []
        console.log('포지션 - 전체 계좌:', accounts)
        
        // KRW는 제외하고 코인만 표시
        let coinAccounts = accounts.filter(acc => acc.currency !== 'KRW' && parseFloat(acc.balance) > 0)
        console.log('포지션 - 보유 코인:', coinAccounts)
        
        // 현재가 정보 가져오기
        const tickerMap = {}
        if (coinAccounts.length > 0) {
          const markets = coinAccounts.map(acc => `KRW-${acc.currency}`).join(',')
          console.log('포지션 - 요청 마켓:', markets)
          try {
            const tickerResponse = await upbitApi.getTicker(markets)
            console.log('포지션 - 티커 응답:', tickerResponse)
            const tickers = tickerResponse.data?.data || []
            console.log('포지션 - 티커 데이터:', tickers)
            
            // 티커를 마켓 코드로 매핑
            if (Array.isArray(tickers) && tickers.length > 0) {
              tickers.forEach(ticker => {
                if (ticker && ticker.market) {
                  tickerMap[ticker.market] = ticker
                }
              })
              console.log('포지션 - 매핑된 티커:', Object.keys(tickerMap))
            }
          } catch (error) {
            console.error('포지션 - 현재가 조회 실패:', error)
            // 에러가 발생해도 계속 진행 (일부 마켓이 존재하지 않을 수 있음)
          }
          
          // 상장폐지된 코인 및 1만원 이하 필터링
          coinAccounts = coinAccounts.filter(account => {
            const market = `KRW-${account.currency}`
            const ticker = tickerMap[market]
            // ticker가 없으면 필터링에서 제외 (상장폐지된 마켓)
            if (!ticker || !ticker.trade_price) {
              console.log(`포지션 필터링 제외: ${account.currency} (상장폐지 또는 존재하지 않는 마켓)`)
              return false
            }
            // 평가액 계산
            const balance = parseFloat(account.balance)
            const currentPrice = ticker.trade_price
            const totalValue = currentPrice * balance
            // 1만원 이하는 제외
            if (totalValue <= 10000) {
              console.log(`포지션 필터링 제외: ${account.currency} (평가액 ${totalValue.toLocaleString()}원 ≤ 1만원)`)
              return false
            }
            console.log(`✅ 포지션 표시: ${account.currency} (평가액 ${totalValue.toLocaleString()}원)`)
            return true
          })
          console.log('포지션 - 필터링 후 코인:', coinAccounts)
        }
        
        // 포지션 데이터 구성
        if (coinAccounts.length > 0) {
          positions.value = coinAccounts.map(account => {
            const market = `KRW-${account.currency}`
            const ticker = tickerMap[market]
            const balance = parseFloat(account.balance)
            const avgBuyPrice = parseFloat(account.avg_buy_price) || 0
            const currentPrice = ticker ? ticker.trade_price : 0
            const profitLoss = (currentPrice - avgBuyPrice) * balance
            const profitLossRate = avgBuyPrice > 0 ? ((currentPrice - avgBuyPrice) / avgBuyPrice) * 100 : 0
            const totalValue = currentPrice * balance
            
            return {
              market: market,
              currency: account.currency,
              balance: balance,
              avg_buy_price: avgBuyPrice,
              current_price: currentPrice,
              profit_loss: profitLoss,
              profit_loss_rate: profitLossRate,
              total_value: totalValue, // 정렬을 위해 추가
              updated_at: new Date().toISOString(),
            }
          })
          
          // 평가액 순서대로 정렬 (내림차순)
          positions.value.sort((a, b) => b.total_value - a.total_value)
          
          console.log('포지션 - 최종 데이터:', positions.value)
        } else {
          positions.value = []
          console.log('포지션 - 데이터 없음')
        }
      } catch (error) {
        console.error('Failed to fetch positions:', error)
        // Upbit API 실패 시 Mock 데이터로 폴백
        try {
          const response = await positionApi.getPositions()
          positions.value = response.data.positions || []
        } catch (fallbackError) {
          positionsError.value = '포지션 정보를 불러오는데 실패했습니다.'
          positions.value = []
        }
      } finally {
        if (showLoading) loadingPositions.value = false
      }
    }

    const fetchTrades = async (showLoading = true) => {
      if (showLoading) loadingTrades.value = true
      tradesError.value = null
      try {
        const response = await tradeApi.getTrades(20, 0)
        trades.value = response.data.trades || []
      } catch (error) {
        console.error('Failed to fetch trades:', error)
        tradesError.value = '거래 내역을 불러오는데 실패했습니다.'
      } finally {
        if (showLoading) loadingTrades.value = false
      }
    }

    const handleStartStrategy = async (strategyId) => {
      loading.value = true
      try {
        await strategyApi.startStrategy(strategyId)
        await fetchStrategies()
        // 팝업 제거 - 상태가 자동으로 업데이트됨
      } catch (error) {
        console.error('Failed to start strategy:', error)
        strategiesError.value = '전략 시작에 실패했습니다: ' + (error.response?.data?.detail || error.message)
      } finally {
        loading.value = false
      }
    }

    const handleStopStrategy = async (strategyId) => {
      loading.value = true
      try {
        await strategyApi.stopStrategy(strategyId)
        await fetchStrategies()
        // 팝업 제거 - 상태가 자동으로 업데이트됨
      } catch (error) {
        console.error('Failed to stop strategy:', error)
        strategiesError.value = '전략 중지에 실패했습니다: ' + (error.response?.data?.detail || error.message)
      } finally {
        loading.value = false
      }
    }

    const fetchVirtualAccount = async (showLoading = true) => {
      try {
        const response = await virtualAccountApi.getBalance()
        virtualAccount.value = response.data.data
      } catch (error) {
        console.error('Failed to fetch virtual account:', error)
      }
    }

    const fetchVirtualTrades = async (showLoading = true) => {
      try {
        const response = await virtualAccountApi.getTrades(20)
        virtualTrades.value = response.data.data || []
      } catch (error) {
        console.error('Failed to fetch virtual trades:', error)
        virtualTrades.value = []
      }
    }

    const fetchStrategyAccounts = async (showLoading = true) => {
      try {
        const response = await virtualAccountApi.getStrategies()
        strategyAccounts.value = response.data.data || []
        // 백엔드에서 이미 prices를 포함하여 반환하므로 별도 조회 불필요
      } catch (error) {
        console.error('Failed to fetch strategy accounts:', error)
        strategyAccounts.value = []
      }
    }

    const refreshAll = async (showLoading = false) => {
      // 스크롤 위치 저장
      const scrollY = window.scrollY
      
      // 자동 새로고침 시에는 loading 표시하지 않음 (깜박임 방지)
      if (showLoading) loading.value = true
      await Promise.all([
        fetchHealth(),
        fetchAccounts(!showLoading),
        fetchStrategies(!showLoading), // 자동 새로고침 시 loading 숨김
        fetchPositions(!showLoading),
        fetchTrades(!showLoading),
        fetchVirtualAccount(!showLoading),
        fetchVirtualTrades(!showLoading),
        fetchStrategyAccounts(!showLoading),
      ])
      if (showLoading) loading.value = false
      
      // 스크롤 위치 복원 (다음 프레임에서 실행하여 DOM 업데이트 후 복원)
      requestAnimationFrame(() => {
        window.scrollTo(0, scrollY)
      })
    }

    // 계좌 관련 헬퍼 함수
    const accountCurrentPrice = (currency) => {
      return accountPrices.value[currency] || 0
    }

    const getAccountProfitLoss = (account) => {
      if (account.currency === 'KRW') return 0
      const currentPrice = accountCurrentPrice(account.currency)
      const avgBuyPrice = parseFloat(account.avg_buy_price || 0)
      const balance = parseFloat(account.balance)
      return (currentPrice - avgBuyPrice) * balance
    }

    const getAccountProfitLossRate = (account) => {
      if (account.currency === 'KRW') return 0
      const currentPrice = accountCurrentPrice(account.currency)
      const avgBuyPrice = parseFloat(account.avg_buy_price || 0)
      if (avgBuyPrice === 0) return 0
      return ((currentPrice - avgBuyPrice) / avgBuyPrice) * 100
    }

    // 가상 계좌 손익 계산 함수
    const getVirtualAccountProfitLoss = (currency, quantity) => {
      if (!virtualAccount.value) return 0
      const currentPrice = virtualAccount.value.prices?.[currency] || 0
      const avgBuyPrice = virtualAccount.value.avg_buy_prices?.[currency] || 0
      if (avgBuyPrice === 0) return 0
      return (currentPrice - avgBuyPrice) * quantity
    }

    const getVirtualAccountProfitLossRate = (currency, quantity) => {
      if (!virtualAccount.value) return 0
      const currentPrice = virtualAccount.value.prices?.[currency] || 0
      const avgBuyPrice = virtualAccount.value.avg_buy_prices?.[currency] || 0
      if (avgBuyPrice === 0) return 0
      return ((currentPrice - avgBuyPrice) / avgBuyPrice) * 100
    }

    // 전략별 계좌 손익 계산 함수
    const getStrategyAccountProfitLoss = (strategyAccount, currency, quantity) => {
      const currentPrice = strategyAccount.prices?.[currency] || strategyAccount.summary?.prices?.[currency] || 0
      const avgBuyPrice = strategyAccount.avg_buy_prices?.[currency] || 0
      if (avgBuyPrice === 0) return 0
      return (currentPrice - avgBuyPrice) * quantity
    }

    const getStrategyAccountProfitLossRate = (strategyAccount, currency, quantity) => {
      const currentPrice = strategyAccount.prices?.[currency] || strategyAccount.summary?.prices?.[currency] || 0
      const avgBuyPrice = strategyAccount.avg_buy_prices?.[currency] || 0
      if (avgBuyPrice === 0) return 0
      return ((currentPrice - avgBuyPrice) / avgBuyPrice) * 100
    }

    // Lifecycle
    onMounted(() => {
      refreshAll(true) // 초기 로드 시에는 loading 표시
      // 30초마다 자동 새로고침 (loading 없이 조용히 업데이트)
      // 1분(60초)마다 자동 새로고침
      setInterval(() => refreshAll(false), 60000)
    })

    return {
      healthData,
      healthStatus,
      healthStatusText,
      strategies,
      positions,
      trades,
      accounts,
      virtualAccount,
      virtualTrades,
      strategyAccounts,
      loading,
      loadingStrategies,
      loadingPositions,
      loadingTrades,
      loadingAccounts,
      strategiesError,
      positionsError,
      tradesError,
      accountsError,
      runningStrategiesCount,
      totalBalance,
      krwBalance,
      accountCurrentPrice,
      getAccountProfitLoss,
      getAccountProfitLossRate,
      getVirtualAccountProfitLoss,
      getVirtualAccountProfitLossRate,
      getStrategyAccountProfitLoss,
      getStrategyAccountProfitLossRate,
      formatUptime,
      formatPrice,
      formatNumber,
      formatDateTime,
      handleStartStrategy,
      handleStopStrategy,
      refreshAll,
    }
  }
}
</script>

