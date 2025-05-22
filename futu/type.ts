type TradeType = "SHARES" | "OPTION";
type Action = "BUY" | "SELL";
type OptionDirection = "CALL" | "PUT";
type Currency = "USD" | "HKD";

type Alert = {
  code: string;
  type: TradeType;
  action: Action;
  direction?: OptionDirection;
  currency?: Currency;
}