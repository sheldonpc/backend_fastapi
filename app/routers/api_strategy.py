import logging
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Request, Depends, HTTPException, status, UploadFile, File

from app.core.templates import templates
from app.deps import get_current_user, get_current_registered_user
from app.schemas import StrategyCreate, StrategyResponse
from app.models import Strategy, User

router = APIRouter(prefix="/admin/api", tags=["strategy"])

from app.utils.logger import get_logger

logger = get_logger("api_strategy")


@router.post("/strategies", response_model=StrategyResponse)
async def strategy_create(
        request: Request,
        strategy_data: StrategyCreate,
        current_user: User = Depends(get_current_registered_user)
):
    """
    创建新策略
    """
    try:
        # 记录接收到的数据
        logger.info(f"用户 {current_user.username} 尝试创建策略: {strategy_data.name}")

        # 验证必填字段
        if not strategy_data.name or strategy_data.name.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="策略名称不能为空"
            )

        if not strategy_data.group_name or strategy_data.group_name.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="策略组别不能为空"
            )

        if not strategy_data.code or strategy_data.code.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="策略代码不能为空"
            )

        if not strategy_data.detail or strategy_data.detail.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="策略详细说明不能为空"
            )

        # 检查策略名称是否已存在
        existing_strategy = await Strategy.filter(
            name=strategy_data.name,
            author_id=current_user.id  # 使用 author_id 而不是 owner_id
        ).first()

        if existing_strategy:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="您已创建过同名的策略"
            )

        # 创建策略对象
        db_strategy = Strategy(
            name=strategy_data.name,
            group_name=strategy_data.group_name,  # 使用 group_name 而不是 group
            icon=strategy_data.icon,
            introduction=strategy_data.introduction,
            code=strategy_data.code,
            detail=strategy_data.detail,
            difficulty=strategy_data.difficulty,
            risk_level=strategy_data.risk_level,
            expected_return=strategy_data.expected_return,
            max_drawdown=strategy_data.max_drawdown,
            sharpe_ratio=strategy_data.sharpe_ratio,
            win_rate=strategy_data.win_rate,
            holding_period=strategy_data.holding_period,
            market_conditions=strategy_data.market_conditions,
            required_indicators=strategy_data.required_indicators,
            tags=strategy_data.tags,
            result_pic=strategy_data.result_pic,
            result_text=strategy_data.result_text,
            publish=strategy_data.publish,
            review=strategy_data.review,
            version=strategy_data.version,
            author_id=current_user.id,  # 使用 author_id 而不是 owner_id
            created_at=datetime.now(),
        )

        # 保存到数据库
        await db_strategy.save()

        logger.info(f"策略 {db_strategy.name} 创建成功，ID: {db_strategy.id}")

        # 返回创建的策略数据
        return {
            "id": db_strategy.id,
            "name": db_strategy.name,
            "group_name": db_strategy.group_name,  # 使用 group_name 而不是 group
            "icon": db_strategy.icon,
            "introduction": db_strategy.introduction,
            "difficulty": db_strategy.difficulty,
            "risk_level": db_strategy.risk_level,
            "expected_return": db_strategy.expected_return,
            "max_drawdown": db_strategy.max_drawdown,
            "sharpe_ratio": db_strategy.sharpe_ratio,
            "win_rate": db_strategy.win_rate,
            "holding_period": db_strategy.holding_period,
            "market_conditions": db_strategy.market_conditions,
            "required_indicators": db_strategy.required_indicators,
            "tags": db_strategy.tags,
            "result_pic": db_strategy.result_pic,
            "result_text": db_strategy.result_text,
            "publish": db_strategy.publish,
            "review": db_strategy.review,
            "version": db_strategy.version,
            "created_at": db_strategy.created_at,
            "updated_at": db_strategy.published_at
        }

    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        # 记录错误并返回通用错误信息
        logger.error(f"创建策略时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建策略时发生内部错误"
        )


@router.get("/strategies", response_model=List[StrategyResponse])
async def get_strategies(
        request: Request,
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_registered_user)
):
    """
    获取当前用户的策略列表
    """
    try:
        # strategies = await Strategy.filter(
        #     author_id=current_user.id  # 使用 author_id 而不是 owner_id
        # ).offset(skip).limit(limit).all()

        strategies = await Strategy.all()

        return strategies
    except Exception as e:
        logger.error(f"获取策略列表时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取策略列表时发生内部错误"
        )


@router.get("/strategies/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
        strategy_id: int,
        request: Request,
        current_user: User = Depends(get_current_registered_user)
):
    """
    获取特定策略详情
    """
    try:
        strategy = await Strategy.filter(
            id=strategy_id,
            author_id=current_user.id  # 使用 author_id 而不是 owner_id
        ).first()

        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="策略不存在"
            )

        return strategy
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取策略详情时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取策略详情时发生内部错误"
        )


@router.put("/strategies/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
        strategy_id: int,
        strategy_update: StrategyCreate,
        request: Request,
        current_user: User = Depends(get_current_registered_user)
):
    """
    更新策略
    """
    try:
        strategy = await Strategy.filter(
            id=strategy_id,
            author_id=current_user.id  # 使用 author_id 而不是 owner_id
        ).first()

        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="策略不存在"
            )

        # 更新字段
        update_data = strategy_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(strategy, field, value)

        await strategy.save()

        logger.info(f"策略 {strategy.name} 更新成功，ID: {strategy.id}")

        return strategy
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新策略时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新策略时发生内部错误"
        )


@router.delete("/strategies/{strategy_id}")
async def delete_strategy(
        strategy_id: int,
        request: Request,
        current_user: User = Depends(get_current_registered_user)
):
    """
    删除策略
    """
    try:
        strategy = await Strategy.filter(
            id=strategy_id,
            author_id=current_user.id  # 使用 author_id 而不是 owner_id
        ).first()

        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="策略不存在"
            )

        await strategy.delete()

        logger.info(f"策略 {strategy.name} 删除成功，ID: {strategy.id}")

        return {"message": "策略删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除策略时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除策略时发生内部错误"
        )
