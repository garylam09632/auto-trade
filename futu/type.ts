type TradeType = "SHARES" | "OPTION";
type Action = "BUY" | "SELL";
type Direction = "CALL" | "PUT";
type Currency = "USD" | "HKD";

type Alert = {
  code: string;
  price: number;
  type: TradeType;
  action: Action;
  direction?: Direction;
  currency?: Currency;
}