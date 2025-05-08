# app/game_state/services/pricing.py

from uuid import UUID
from app.game_state.entities.item import Item
from app.game_state.entities.settlement import Settlement
#from app.game_state.entities.trader_entity import Trader
from app.game_state.repositories.settlement_repository import SettlementRepository
#from app.game_state.repositories.trader_repo import TraderRepo
#from app.game_state.services.reputation import ReputationService
#from app.game_state.services.discount_policies import (
#    SettlementDiscountPolicy,
#    TraderDiscountPolicy,
#)
#from app.game_state.services.race_pricing import RacePricePolicy
#from app.game_state.services.faction_pricing import FactionSurchargePolicy
#from app.game_state.services.theme import ThemeService
from app.game_state.enums.theme import Theme
from app.game_state.enums.race import Race

class PricingService:
    @staticmethod
    def price_for(
        item: Item,
        player_id: UUID,
        settlement_id: UUID,
        trader_id: UUID,
        player_race: Race,
        theme: Theme,
    ) -> float:
        base = item.base_price or 0.0

        # 1) Settlement & Trader entities (to read disliked_faction_ids)
        settlement = SettlementRepository().get(settlement_id)
        trader     = TraderRepo().get(trader_id)

        # 2) Reputations
        rep_set = ReputationService.for_settlement(player_id, settlement_id)
        rep_trd = ReputationService.for_trader(player_id, trader_id)

        # 3) Discounts from rep
        disc_set = SettlementDiscountPolicy.get_for(rep_set)
        disc_trd = TraderDiscountPolicy.get_for(rep_trd)

        # 4) Race modifier (only if player_race ∈ current theme)
        if player_race not in ThemeService.races_for(theme):
            raise ValueError(f"{player_race} not valid in theme {theme}")
        race_mod = RacePricePolicy.get_for(player_race)

        # 5) Faction surcharges: take the worst (most negative) across all disliked factions
        faction_surcharges = []
        for faction_id in settlement.disliked_faction_ids + trader.disliked_faction_ids:
            rep_f = ReputationService.for_faction(player_id, faction_id)
            faction_surcharges.append(FactionSurchargePolicy.get_for(rep_f))
        # default surcharge 0.0 if no disliked factions
        fac_mod = min(faction_surcharges) if faction_surcharges else 0.0

        # 6) Combine multiplicatively:
        price = base \
            * (1 - disc_set) \
            * (1 - disc_trd) \
            * (1 - race_mod) \
            * (1 - fac_mod)

        return round(price, 2)
