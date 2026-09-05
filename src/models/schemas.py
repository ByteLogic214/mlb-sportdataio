"""
Modelos de datos Pydantic para tipado estático y validación de respuestas API.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class Stadium(BaseModel):
    StadiumID: int
    Name: Optional[str] = None
    City: Optional[str] = None
    State: Optional[str] = None
    Country: Optional[str] = None
    Capacity: Optional[int] = None
    PlayingSurface: Optional[str] = None
    LeftField: Optional[int] = None
    MidLeftField: Optional[int] = None
    LeftCenterField: Optional[int] = None
    MidLeftCenterField: Optional[int] = None
    CenterField: Optional[int] = None
    MidRightCenterField: Optional[int] = None
    RightCenterField: Optional[int] = None
    MidRightField: Optional[int] = None
    RightField: Optional[int] = None
    Altitude: Optional[int] = None
    HomePlateDirection: Optional[int] = None
    Type: Optional[str] = None


class Team(BaseModel):
    TeamID: int
    Key: str
    Active: bool
    City: Optional[str] = None
    Name: Optional[str] = None
    StadiumID: Optional[int] = None
    League: Optional[str] = None
    Division: Optional[str] = None
    PrimaryColor: Optional[str] = None
    SecondaryColor: Optional[str] = None
    TertiaryColor: Optional[str] = None
    QuaternaryColor: Optional[str] = None
    WikipediaLogoUrl: Optional[str] = None
    WikipediaWordMarkUrl: Optional[str] = None
    GlobalTeamID: Optional[int] = None


class Game(BaseModel):
    GameID: int
    Season: int
    SeasonType: int
    Status: Optional[str] = None
    Day: Optional[datetime] = None
    DateTime: Optional[datetime] = None
    AwayTeam: Optional[str] = None
    HomeTeam: Optional[str] = None
    AwayTeamID: Optional[int] = None
    HomeTeamID: Optional[int] = None
    AwayTeamMoneyLine: Optional[int] = None
    HomeTeamMoneyLine: Optional[int] = None
    PointSpread: Optional[float] = None
    OverUnder: Optional[float] = None
    AwayTeamRuns: Optional[int] = None
    HomeTeamRuns: Optional[int] = None
    StadiumID: Optional[int] = None
    Channel: Optional[str] = None
    Inning: Optional[int] = None
    InningHalf: Optional[str] = None
    Outs: Optional[int] = None
    Balls: Optional[int] = None
    Strikes: Optional[int] = None
    CurrentPitcherID: Optional[int] = None
    CurrentHitterID: Optional[int] = None
    AwayTeamStartingPitcherID: Optional[int] = None
    HomeTeamStartingPitcherID: Optional[int] = None
    AwayTeamStartingPitcher: Optional[str] = None
    HomeTeamStartingPitcher: Optional[str] = None
    WinningPitcherID: Optional[int] = None
    LosingPitcherID: Optional[int] = None
    SavingPitcherID: Optional[int] = None
    Weather: Optional[str] = None
    Temperature: Optional[int] = None
    Humidity: Optional[int] = None
    WindSpeed: Optional[int] = None
    WindDirection: Optional[str] = None
    RescheduledFromGameID: Optional[int] = None
    RescheduledGameID: Optional[int] = None
    IsClosed: bool = False
    Updated: Optional[datetime] = None

    @field_validator("Day", "DateTime", "Updated", mode="before")
    @classmethod
    def parse_datetime(cls, v):
        if v is None or isinstance(v, datetime):
            return v
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%Y-%b-%d"):
            try:
                return datetime.strptime(v, fmt)
            except ValueError:
                continue
        return v


class PlayerBasic(BaseModel):
    PlayerID: int
    SportsDataID: Optional[str] = None
    Status: Optional[str] = None
    TeamID: Optional[int] = None
    Team: Optional[str] = None
    Jersey: Optional[int] = None
    PositionCategory: Optional[str] = None
    Position: Optional[str] = None
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    BatHand: Optional[str] = None
    ThrowHand: Optional[str] = None
    Height: Optional[int] = None
    Weight: Optional[int] = None
    BirthDate: Optional[datetime] = None
    BirthCity: Optional[str] = None
    BirthState: Optional[str] = None
    BirthCountry: Optional[str] = None
    HighSchool: Optional[str] = None
    College: Optional[str] = None
    ProDebut: Optional[str] = None
    Salary: Optional[int] = None
    PhotoUrl: Optional[str] = None
    SportRadarPlayerID: Optional[str] = None
    RotoworldPlayerID: Optional[int] = None
    RotoWirePlayerID: Optional[int] = None
    FantasyAlarmPlayerID: Optional[int] = None
    StatsPlayerID: Optional[int] = None
    SportsDirectPlayerID: Optional[int] = None
    XmlTeamPlayerID: Optional[int] = None
    InjuryStatus: Optional[str] = None
    InjuryBodyPart: Optional[str] = None
    InjuryStartDate: Optional[datetime] = None
    InjuryNotes: Optional[str] = None
    FanDuelPlayerID: Optional[int] = None
    DraftKingsPlayerID: Optional[int] = None
    YahooPlayerID: Optional[int] = None
    FanDuelName: Optional[str] = None
    DraftKingsName: Optional[str] = None
    YahooName: Optional[str] = None
    GlobalTeamID: Optional[int] = None


class PlayerSeasonStats(BaseModel):
    StatID: Optional[int] = None
    TeamID: Optional[int] = None
    PlayerID: int
    SeasonType: Optional[int] = None
    Season: Optional[int] = None
    Name: Optional[str] = None
    Team: Optional[str] = None
    Position: Optional[str] = None
    PositionCategory: Optional[str] = None
    Games: Optional[int] = 0
    Started: Optional[int] = 0
    AtBats: Optional[int] = 0
    Runs: Optional[int] = 0
    Hits: Optional[int] = 0
    Singles: Optional[int] = 0
    Doubles: Optional[int] = 0
    Triples: Optional[int] = 0
    HomeRuns: Optional[int] = 0
    RunsBattedIn: Optional[int] = 0
    BattingAverage: Optional[float] = 0.0
    OnBasePercentage: Optional[float] = 0.0
    SluggingPercentage: Optional[float] = 0.0
    OnBasePlusSlugging: Optional[float] = 0.0
    IsolatedPower: Optional[float] = 0.0
    TotalBases: Optional[int] = 0
    Strikeouts: Optional[int] = 0
    Walks: Optional[int] = 0
    HitByPitch: Optional[int] = 0
    Sacrifices: Optional[int] = 0
    SacrificeFlies: Optional[int] = 0
    GroundIntoDoublePlay: Optional[int] = 0
    StolenBases: Optional[int] = 0
    CaughtStealing: Optional[int] = 0
    LeftOnBase: Optional[int] = 0
    PlateAppearances: Optional[int] = 0
    PitchesSeen: Optional[int] = 0
    WeightedOnBasePercentage: Optional[float] = 0.0
    BattingAverageOnBallsInPlay: Optional[float] = 0.0
    GroundOuts: Optional[int] = 0
    FlyOuts: Optional[int] = 0
    LineOuts: Optional[int] = 0
    PopOuts: Optional[int] = 0
    ReachedOnError: Optional[int] = 0
    InningsPitchedDecimal: Optional[float] = 0.0
    InningsPitchedFull: Optional[int] = 0
    InningsPitchedOuts: Optional[int] = 0
    TotalOutsPitched: Optional[int] = 0
    Wins: Optional[int] = 0
    Losses: Optional[int] = 0
    EarnedRunAverage: Optional[float] = 0.0
    PitchingHits: Optional[int] = 0
    PitchingRuns: Optional[int] = 0
    PitchingEarnedRuns: Optional[int] = 0
    PitchingHomeRuns: Optional[int] = 0
    PitchingStrikeouts: Optional[int] = 0
    PitchingWalks: Optional[int] = 0
    PitchingBattingAverageAgainst: Optional[float] = 0.0
    PitchingOnBasePercentage: Optional[float] = 0.0
    PitchingSluggingPercentage: Optional[float] = 0.0
    PitchingOnBasePlusSlugging: Optional[float] = 0.0
    PitchingTotalBases: Optional[int] = 0
    PitchingSingles: Optional[int] = 0
    PitchingDoubles: Optional[int] = 0
    PitchingTriples: Optional[int] = 0
    PitchingGroundOuts: Optional[int] = 0
    PitchingFlyOuts: Optional[int] = 0
    PitchingLineOuts: Optional[int] = 0
    PitchingPopOuts: Optional[int] = 0
    PitchingIntentionalWalks: Optional[int] = 0
    PitchingHitByPitch: Optional[int] = 0
    PitchingSacrifices: Optional[int] = 0
    PitchingSacrificeFlies: Optional[int] = 0
    PitchingPlateAppearances: Optional[int] = 0
    PitchingInningStarted: Optional[int] = 0
    PitchingQualityStarts: Optional[int] = 0
    PitchingBlownSaves: Optional[int] = 0
    PitchingHolds: Optional[int] = 0
    Saves: Optional[int] = 0
    ShutOuts: Optional[int] = 0
    PitchingNoHitters: Optional[int] = 0
    PitchingPerfectGames: Optional[int] = 0
    PitchingGroundIntoDoublePlay: Optional[int] = 0
    PitchingReachedOnError: Optional[int] = 0
    PitchingCatchersInterference: Optional[int] = 0
    WalksHitsPerInningsPitched: Optional[float] = 0.0
    PitchingBattingAverageOnBallsInPlay: Optional[float] = 0.0
    PitchingWeightedOnBasePercentage: Optional[float] = 0.0
    StrikeoutsPerNineInnings: Optional[float] = 0.0
    WalksPerNineInnings: Optional[float] = 0.0
    FieldingIndependentPitching: Optional[float] = 0.0
    Errors: Optional[int] = 0
    DoublePlays: Optional[int] = 0
    FantasyPoints: Optional[float] = 0.0
    Updated: Optional[datetime] = None


class PlayerGameStats(BaseModel):
    StatID: Optional[int] = None
    TeamID: Optional[int] = None
    PlayerID: int
    SeasonType: Optional[int] = None
    Season: Optional[int] = None
    GameID: Optional[int] = None
    Name: Optional[str] = None
    Team: Optional[str] = None
    Position: Optional[str] = None
    PositionCategory: Optional[str] = None
    Started: Optional[int] = 0
    Games: Optional[int] = 0
    BattingOrder: Optional[int] = None
    BattingOrderConfirmed: Optional[bool] = None
    FanDuelSalary: Optional[int] = None
    DraftKingsSalary: Optional[int] = None
    FantasyDataSalary: Optional[int] = None
    YahooSalary: Optional[int] = None
    InjuryStatus: Optional[str] = None
    InjuryBodyPart: Optional[str] = None
    InjuryStartDate: Optional[datetime] = None
    InjuryNotes: Optional[str] = None
    FanDuelPosition: Optional[str] = None
    DraftKingsPosition: Optional[str] = None
    YahooPosition: Optional[str] = None
    AtBats: Optional[int] = 0
    Runs: Optional[int] = 0
    Hits: Optional[int] = 0
    Singles: Optional[int] = 0
    Doubles: Optional[int] = 0
    Triples: Optional[int] = 0
    HomeRuns: Optional[int] = 0
    RunsBattedIn: Optional[int] = 0
    BattingAverage: Optional[float] = 0.0
    OnBasePercentage: Optional[float] = 0.0
    SluggingPercentage: Optional[float] = 0.0
    OnBasePlusSlugging: Optional[float] = 0.0
    IsolatedPower: Optional[float] = 0.0
    TotalBases: Optional[int] = 0
    Strikeouts: Optional[int] = 0
    Walks: Optional[int] = 0
    HitByPitch: Optional[int] = 0
    Sacrifices: Optional[int] = 0
    SacrificeFlies: Optional[int] = 0
    GroundIntoDoublePlay: Optional[int] = 0
    StolenBases: Optional[int] = 0
    CaughtStealing: Optional[int] = 0
    LeftOnBase: Optional[int] = 0
    PlateAppearances: Optional[int] = 0
    PitchesSeen: Optional[int] = 0
    WeightedOnBasePercentage: Optional[float] = 0.0
    BattingAverageOnBallsInPlay: Optional[float] = 0.0
    GroundOuts: Optional[int] = 0
    FlyOuts: Optional[int] = 0
    LineOuts: Optional[int] = 0
    PopOuts: Optional[int] = 0
    ReachedOnError: Optional[int] = 0
    InningsPitchedDecimal: Optional[float] = 0.0
    InningsPitchedFull: Optional[int] = 0
    InningsPitchedOuts: Optional[int] = 0
    TotalOutsPitched: Optional[int] = 0
    Wins: Optional[int] = 0
    Losses: Optional[int] = 0
    EarnedRunAverage: Optional[float] = 0.0
    PitchingHits: Optional[int] = 0
    PitchingRuns: Optional[int] = 0
    PitchingEarnedRuns: Optional[int] = 0
    PitchingHomeRuns: Optional[int] = 0
    PitchingStrikeouts: Optional[int] = 0
    PitchingWalks: Optional[int] = 0
    PitchingBattingAverageAgainst: Optional[float] = 0.0
    PitchingOnBasePercentage: Optional[float] = 0.0
    PitchingSluggingPercentage: Optional[float] = 0.0
    PitchingOnBasePlusSlugging: Optional[float] = 0.0
    PitchingTotalBases: Optional[int] = 0
    PitchingSingles: Optional[int] = 0
    PitchingDoubles: Optional[int] = 0
    PitchingTriples: Optional[int] = 0
    PitchingGroundOuts: Optional[int] = 0
    PitchingFlyOuts: Optional[int] = 0
    PitchingLineOuts: Optional[int] = 0
    PitchingPopOuts: Optional[int] = 0
    PitchingIntentionalWalks: Optional[int] = 0
    PitchingHitByPitch: Optional[int] = 0
    PitchingSacrifices: Optional[int] = 0
    PitchingSacrificeFlies: Optional[int] = 0
    PitchingPlateAppearances: Optional[int] = 0
    PitchingInningStarted: Optional[int] = 0
    PitchingQualityStarts: Optional[int] = 0
    PitchingBlownSaves: Optional[int] = 0
    PitchingHolds: Optional[int] = 0
    Saves: Optional[int] = 0
    ShutOuts: Optional[int] = 0
    PitchingNoHitters: Optional[int] = 0
    PitchingPerfectGames: Optional[int] = 0
    PitchingGroundIntoDoublePlay: Optional[int] = 0
    PitchingReachedOnError: Optional[int] = 0
    PitchingCatchersInterference: Optional[int] = 0
    WalksHitsPerInningsPitched: Optional[float] = 0.0
    PitchingBattingAverageOnBallsInPlay: Optional[float] = 0.0
    PitchingWeightedOnBasePercentage: Optional[float] = 0.0
    StrikeoutsPerNineInnings: Optional[float] = 0.0
    WalksPerNineInnings: Optional[float] = 0.0
    FieldingIndependentPitching: Optional[float] = 0.0
    Errors: Optional[int] = 0
    DoublePlays: Optional[int] = 0
    FantasyPoints: Optional[float] = 0.0
    FantasyPointsFanDuel: Optional[float] = 0.0
    FantasyPointsDraftKings: Optional[float] = 0.0
    FantasyPointsYahoo: Optional[float] = 0.0
    FantasyPointsBatting: Optional[float] = 0.0
    FantasyPointsPitching: Optional[float] = 0.0
    Updated: Optional[datetime] = None
    DateTime: Optional[datetime] = None
    Day: Optional[datetime] = None
    HomeOrAway: Optional[str] = None
    IsGameOver: Optional[bool] = None
    GlobalGameID: Optional[int] = None
    GlobalTeamID: Optional[int] = None
    GlobalOpponentID: Optional[int] = None
    OpponentID: Optional[int] = None
    Opponent: Optional[str] = None
    OpponentRank: Optional[int] = None
    OpponentPositionRank: Optional[int] = None


class LineupPlayer(BaseModel):
    PlayerID: int
    Name: Optional[str] = None
    Position: Optional[str] = None
    BattingOrder: Optional[int] = None
    BatHand: Optional[str] = None


class StartingLineup(BaseModel):
    GameID: int
    DateTime: Optional[datetime] = None
    Status: Optional[str] = None
    Team: Optional[str] = None
    TeamID: Optional[int] = None
    Players: List[LineupPlayer] = Field(default_factory=list)


class PlayerGameProjection(BaseModel):
    StatID: Optional[int] = None
    TeamID: Optional[int] = None
    PlayerID: int
    SeasonType: Optional[int] = None
    Season: Optional[int] = None
    GameID: Optional[int] = None
    Name: Optional[str] = None
    Team: Optional[str] = None
    Position: Optional[str] = None
    PositionCategory: Optional[str] = None
    BattingOrder: Optional[int] = None
    BattingOrderConfirmed: Optional[bool] = None
    FanDuelSalary: Optional[int] = None
    DraftKingsSalary: Optional[int] = None
    FantasyDataSalary: Optional[int] = None
    YahooSalary: Optional[int] = None
    InjuryStatus: Optional[str] = None
    FanDuelPosition: Optional[str] = None
    DraftKingsPosition: Optional[str] = None
    YahooPosition: Optional[str] = None
    AtBats: Optional[float] = 0.0
    Runs: Optional[float] = 0.0
    Hits: Optional[float] = 0.0
    Singles: Optional[float] = 0.0
    Doubles: Optional[float] = 0.0
    Triples: Optional[float] = 0.0
    HomeRuns: Optional[float] = 0.0
    RunsBattedIn: Optional[float] = 0.0
    BattingAverage: Optional[float] = 0.0
    OnBasePercentage: Optional[float] = 0.0
    SluggingPercentage: Optional[float] = 0.0
    OnBasePlusSlugging: Optional[float] = 0.0
    TotalBases: Optional[float] = 0.0
    Strikeouts: Optional[float] = 0.0
    Walks: Optional[float] = 0.0
    HitByPitch: Optional[float] = 0.0
    Sacrifices: Optional[float] = 0.0
    SacrificeFlies: Optional[float] = 0.0
    GroundIntoDoublePlay: Optional[float] = 0.0
    StolenBases: Optional[float] = 0.0
    CaughtStealing: Optional[float] = 0.0
    PlateAppearances: Optional[float] = 0.0
    PitchesSeen: Optional[float] = 0.0
    WeightedOnBasePercentage: Optional[float] = 0.0
    BattingAverageOnBallsInPlay: Optional[float] = 0.0
    GroundOuts: Optional[float] = 0.0
    FlyOuts: Optional[float] = 0.0
    LineOuts: Optional[float] = 0.0
    PopOuts: Optional[float] = 0.0
    ReachedOnError: Optional[float] = 0.0
    InningsPitchedDecimal: Optional[float] = 0.0
    Wins: Optional[float] = 0.0
    Losses: Optional[float] = 0.0
    EarnedRunAverage: Optional[float] = 0.0
    PitchingHits: Optional[float] = 0.0
    PitchingRuns: Optional[float] = 0.0
    PitchingEarnedRuns: Optional[float] = 0.0
    PitchingHomeRuns: Optional[float] = 0.0
    PitchingStrikeouts: Optional[float] = 0.0
    PitchingWalks: Optional[float] = 0.0
    PitchingBattingAverageAgainst: Optional[float] = 0.0
    PitchingOnBasePercentage: Optional[float] = 0.0
    PitchingSluggingPercentage: Optional[float] = 0.0
    PitchingOnBasePlusSlugging: Optional[float] = 0.0
    PitchingTotalBases: Optional[float] = 0.0
    PitchingSingles: Optional[float] = 0.0
    PitchingDoubles: Optional[float] = 0.0
    PitchingTriples: Optional[float] = 0.0
    PitchingGroundOuts: Optional[float] = 0.0
    PitchingFlyOuts: Optional[float] = 0.0
    PitchingLineOuts: Optional[float] = 0.0
    PitchingPopOuts: Optional[float] = 0.0
    PitchingIntentionalWalks: Optional[float] = 0.0
    PitchingHitByPitch: Optional[float] = 0.0
    PitchingSacrifices: Optional[float] = 0.0
    PitchingSacrificeFlies: Optional[float] = 0.0
    PitchingPlateAppearances: Optional[float] = 0.0
    PitchingInningStarted: Optional[float] = 0.0
    PitchingQualityStarts: Optional[float] = 0.0
    PitchingBlownSaves: Optional[float] = 0.0
    PitchingHolds: Optional[float] = 0.0
    Saves: Optional[float] = 0.0
    ShutOuts: Optional[float] = 0.0
    PitchingNoHitters: Optional[float] = 0.0
    PitchingPerfectGames: Optional[float] = 0.0
    PitchingGroundIntoDoublePlay: Optional[float] = 0.0
    PitchingReachedOnError: Optional[float] = 0.0
    PitchingCatchersInterference: Optional[float] = 0.0
    WalksHitsPerInningsPitched: Optional[float] = 0.0
    PitchingBattingAverageOnBallsInPlay: Optional[float] = 0.0
    PitchingWeightedOnBasePercentage: Optional[float] = 0.0
    StrikeoutsPerNineInnings: Optional[float] = 0.0
    WalksPerNineInnings: Optional[float] = 0.0
    FieldingIndependentPitching: Optional[float] = 0.0
    FantasyPoints: Optional[float] = 0.0
    FantasyPointsFanDuel: Optional[float] = 0.0
    FantasyPointsDraftKings: Optional[float] = 0.0
    FantasyPointsYahoo: Optional[float] = 0.0
    FantasyPointsBatting: Optional[float] = 0.0
    FantasyPointsPitching: Optional[float] = 0.0
    DateTime: Optional[datetime] = None
    Day: Optional[datetime] = None


class TeamGameStats(BaseModel):
    StatID: Optional[int] = None
    TeamID: int
    SeasonType: Optional[int] = None
    Season: Optional[int] = None
    GameID: Optional[int] = None
    Name: Optional[str] = None
    Team: Optional[str] = None
    AtBats: Optional[int] = 0
    Runs: Optional[int] = 0
    Hits: Optional[int] = 0
    Singles: Optional[int] = 0
    Doubles: Optional[int] = 0
    Triples: Optional[int] = 0
    HomeRuns: Optional[int] = 0
    RunsBattedIn: Optional[int] = 0
    BattingAverage: Optional[float] = 0.0
    OnBasePercentage: Optional[float] = 0.0
    SluggingPercentage: Optional[float] = 0.0
    OnBasePlusSlugging: Optional[float] = 0.0
    IsolatedPower: Optional[float] = 0.0
    TotalBases: Optional[int] = 0
    Strikeouts: Optional[int] = 0
    Walks: Optional[int] = 0
    HitByPitch: Optional[int] = 0
    Sacrifices: Optional[int] = 0
    SacrificeFlies: Optional[int] = 0
    GroundIntoDoublePlay: Optional[int] = 0
    StolenBases: Optional[int] = 0
    CaughtStealing: Optional[int] = 0
    LeftOnBase: Optional[int] = 0
    PlateAppearances: Optional[int] = 0
    PitchesSeen: Optional[int] = 0
    WeightedOnBasePercentage: Optional[float] = 0.0
    BattingAverageOnBallsInPlay: Optional[float] = 0.0
    GroundOuts: Optional[int] = 0
    FlyOuts: Optional[int] = 0
    LineOuts: Optional[int] = 0
    PopOuts: Optional[int] = 0
    ReachedOnError: Optional[int] = 0
    InningsPitchedDecimal: Optional[float] = 0.0
    Wins: Optional[int] = 0
    Losses: Optional[int] = 0
    EarnedRunAverage: Optional[float] = 0.0
    PitchingHits: Optional[int] = 0
    PitchingRuns: Optional[int] = 0
    PitchingEarnedRuns: Optional[int] = 0
    PitchingHomeRuns: Optional[int] = 0
    PitchingStrikeouts: Optional[int] = 0
    PitchingWalks: Optional[int] = 0
    PitchingBattingAverageAgainst: Optional[float] = 0.0
    PitchingOnBasePercentage: Optional[float] = 0.0
    PitchingSluggingPercentage: Optional[float] = 0.0
    PitchingOnBasePlusSlugging: Optional[float] = 0.0
    PitchingTotalBases: Optional[int] = 0
    PitchingSingles: Optional[int] = 0
    PitchingDoubles: Optional[int] = 0
    PitchingTriples: Optional[int] = 0
    PitchingGroundOuts: Optional[int] = 0
    PitchingFlyOuts: Optional[int] = 0
    PitchingLineOuts: Optional[int] = 0
    PitchingPopOuts: Optional[int] = 0
    PitchingIntentionalWalks: Optional[int] = 0
    PitchingHitByPitch: Optional[int] = 0
    PitchingSacrifices: Optional[int] = 0
    PitchingSacrificeFlies: Optional[int] = 0
    PitchingPlateAppearances: Optional[int] = 0
    PitchingInningStarted: Optional[int] = 0
    PitchingQualityStarts: Optional[int] = 0
    PitchingBlownSaves: Optional[int] = 0
    PitchingHolds: Optional[int] = 0
    Saves: Optional[int] = 0
    ShutOuts: Optional[int] = 0
    PitchingNoHitters: Optional[int] = 0
    PitchingPerfectGames: Optional[int] = 0
    PitchingGroundIntoDoublePlay: Optional[int] = 0
    PitchingReachedOnError: Optional[int] = 0
    PitchingCatchersInterference: Optional[int] = 0
    WalksHitsPerInningsPitched: Optional[float] = 0.0
    PitchingBattingAverageOnBallsInPlay: Optional[float] = 0.0
    PitchingWeightedOnBasePercentage: Optional[float] = 0.0
    StrikeoutsPerNineInnings: Optional[float] = 0.0
    WalksPerNineInnings: Optional[float] = 0.0
    FieldingIndependentPitching: Optional[float] = 0.0
    Errors: Optional[int] = 0
    DoublePlays: Optional[int] = 0
    FantasyPoints: Optional[float] = 0.0
    Updated: Optional[datetime] = None
    DateTime: Optional[datetime] = None
    Day: Optional[datetime] = None
    HomeOrAway: Optional[str] = None
    IsGameOver: Optional[bool] = None
    GlobalGameID: Optional[int] = None
    GlobalTeamID: Optional[int] = None
    GlobalOpponentID: Optional[int] = None
    OpponentID: Optional[int] = None
    Opponent: Optional[str] = None
    OpponentRank: Optional[int] = None
    OpponentPositionRank: Optional[int] = None


class BoxScore(BaseModel):
    Game: Optional[Game] = None
    Innings: Optional[List[Dict[str, Any]]] = None
    TeamGames: Optional[List[TeamGameStats]] = None
    PlayerGames: Optional[List[PlayerGameStats]] = None


class TeamProjection(BaseModel):
    team: str
    team_name: str
    x_runs: float = Field(..., description="Carreras esperadas")
    x_runs_std: float = Field(..., description="Desviación estándar de carreras")
    x_runs_distribution: Optional[Dict[int, float]] = Field(default=None, description="PMF de carreras (0-15)")
    offense_rating: float = Field(..., description="Rating ofensivo ajustado")
    defense_rating: float = Field(..., description="Rating defensivo ajustado")
    park_factor_runs: float = 1.0
    weather_factor: float = 1.0
    bullpen_fatigue_penalty: float = 0.0


class MoneylineProjection(BaseModel):
    game_id: int
    date: datetime
    away_team: str
    home_team: str
    away_x_runs: float
    home_x_runs: float
    away_win_prob: float = Field(..., ge=0.0, le=1.0)
    home_win_prob: float = Field(..., ge=0.0, le=1.0)
    away_ml_fair_odds: float
    home_ml_fair_odds: float
    away_ml_implied_prob: Optional[float] = None
    home_ml_implied_prob: Optional[float] = None
    away_edge: Optional[float] = None
    home_edge: Optional[float] = None
    total_x_runs: float
    over_prob: float
    under_prob: float
    over_fair_odds: float
    under_fair_odds: float
    over_under_line: Optional[float] = None
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    simulation_method: str = "monte_carlo"


class PlayerHitProjection(BaseModel):
    game_id: int
    player_id: int
    player_name: str
    team: str
    opponent: str
    batting_order: Optional[int] = None
    bat_hand: Optional[str] = None
    opponent_pitcher_hand: Optional[str] = None
    x_pa: float = Field(..., description="Apariciones al plato esperadas")
    x_hits: float = Field(..., description="Hits esperados")
    hit_prob_per_pa: float = Field(..., ge=0.0, le=1.0)
    hit_prob_over_0_5: float = Field(..., ge=0.0, le=1.0)
    hit_prob_over_1_5: float = Field(..., ge=0.0, le=1.0)
    hit_prob_exactly_0: float = Field(..., ge=0.0, le=1.0)
    hit_prob_exactly_1: float = Field(..., ge=0.0, le=1.0)
    hit_prob_exactly_2: float = Field(..., ge=0.0, le=1.0)
    hit_prob_exactly_3_plus: float = Field(..., ge=0.0, le=1.0)
    woba_vs_hand: float
    woba_pitcher_vs_hand: float
    platoon_advantage: bool
    park_factor_hits: float = 1.0
    lineup_spot_pa_factor: float = 1.0
    recommendation: Optional[str] = None
    edge_over_0_5: Optional[float] = None
    edge_over_1_5: Optional[float] = None
    confidence_score: float = Field(..., ge=0.0, le=1.0)


class DailyProjectionOutput(BaseModel):
    date: datetime
    games_projected: int
    moneyline_projections: List[MoneylineProjection]
    team_total_projections: List[TeamProjection]
    player_hit_projections: List[PlayerHitProjection]
    generated_at: datetime
    model_version: str = "1.0.0"
