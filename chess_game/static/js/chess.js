class ChessGame {
    constructor() {
        this.board = document.getElementById('chessboard');
        this.statusMessage = document.getElementById('status-message');
        this.resetButton = document.getElementById('reset-game');
        this.selectedSquare = null;
        this.validMoves = [];
        
        this.initializeBoard();
        this.setupEventListeners();
    }
    
    initializeBoard() {
        this.board.innerHTML = '';
        for (let row = 7; row >= 0; row--) {
            for (let col = 0; col < 8; col++) {
                const square = document.createElement('div');
                square.className = `square ${(row + col) % 2 === 0 ? 'light' : 'dark'}`;
                square.dataset.position = `${col}${row}`;
                this.board.appendChild(square);
            }
        }
        this.setupInitialPieces();
    }
    
    setupInitialPieces() {
        const pieces = {
            '00': 'white-rook', '10': 'white-knight', '20': 'white-bishop', '30': 'white-queen',
            '40': 'white-king', '50': 'white-bishop', '60': 'white-knight', '70': 'white-rook',
            '01': 'white-pawn', '11': 'white-pawn', '21': 'white-pawn', '31': 'white-pawn',
            '41': 'white-pawn', '51': 'white-pawn', '61': 'white-pawn', '71': 'white-pawn',
            '06': 'black-pawn', '16': 'black-pawn', '26': 'black-pawn', '36': 'black-pawn',
            '46': 'black-pawn', '56': 'black-pawn', '66': 'black-pawn', '76': 'black-pawn',
            '07': 'black-rook', '17': 'black-knight', '27': 'black-bishop', '37': 'black-queen',
            '47': 'black-king', '57': 'black-bishop', '67': 'black-knight', '77': 'black-rook'
        };
        
        for (const [position, piece] of Object.entries(pieces)) {
            this.placePiece(position, piece);
        }
    }
    
    placePiece(position, pieceType) {
        const square = this.board.querySelector(`[data-position="${position}"]`);
        const piece = document.createElement('img');
        piece.className = 'piece';
        piece.src = `/static/images/${pieceType}.svg`;
        piece.dataset.pieceType = pieceType;
        square.appendChild(piece);
    }
    
    setupEventListeners() {
        this.board.addEventListener('click', (e) => this.handleSquareClick(e));
        this.resetButton.addEventListener('click', () => this.resetGame());
    }
    
    async handleSquareClick(event) {
        const square = event.target.closest('.square');
        if (!square) return;
        
        const position = square.dataset.position;
        
        if (this.selectedSquare === null) {
            if (square.querySelector('.piece')) {
                this.selectSquare(square);
                await this.showValidMoves(position);
            }
        } else {
            if (this.validMoves.includes(position)) {
                await this.makeMove(this.selectedSquare.dataset.position, position);
            }
            this.clearSelection();
        }
    }
    
    selectSquare(square) {
        this.clearSelection();
        square.classList.add('selected');
        this.selectedSquare = square;
    }
    
    async showValidMoves(position) {
        try {
            const response = await fetch('/get_valid_moves', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ position }),
            });
            
            const data = await response.json();
            this.validMoves = data.valid_moves;
            
            this.validMoves.forEach(pos => {
                const square = this.board.querySelector(`[data-position="${pos}"]`);
                square.classList.add('valid-move');
            });
        } catch (error) {
            console.error('Error getting valid moves:', error);
        }
    }
    
    clearSelection() {
        if (this.selectedSquare) {
            this.selectedSquare.classList.remove('selected');
            this.selectedSquare = null;
        }
        
        document.querySelectorAll('.valid-move').forEach(square => {
            square.classList.remove('valid-move');
        });
        
        this.validMoves = [];
    }
    
    async makeMove(fromPos, toPos) {
        try {
            const response = await fetch('/make_move', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ from: fromPos, to: toPos }),
            });
            
            const data = await response.json();
            
            if (data.valid) {
                await this.animateMove(fromPos, toPos);
                
                if (data.captured) {
                    const capturedPiece = this.board.querySelector(`[data-position="${toPos}"] .piece`);
                    if (capturedPiece) {
                        capturedPiece.classList.add('captured');
                        await new Promise(resolve => setTimeout(resolve, 300));
                        capturedPiece.remove();
                    }
                }
                
                if (data.ai_move) {
                    await new Promise(resolve => setTimeout(resolve, 500));
                    await this.makeMove(data.ai_move.from, data.ai_move.to);
                }
                
                this.updateGameStatus(data.game_status);
            }
        } catch (error) {
            console.error('Error making move:', error);
        }
    }
    
    async animateMove(fromPos, toPos) {
        const fromSquare = this.board.querySelector(`[data-position="${fromPos}"]`);
        const toSquare = this.board.querySelector(`[data-position="${toPos}"]`);
        const piece = fromSquare.querySelector('.piece');
        
        if (piece) {
            toSquare.appendChild(piece);
        }
    }
    
    updateGameStatus(status) {
        if (status === 'checkmate') {
            this.statusMessage.textContent = 'Checkmate!';
        } else if (status === 'stalemate') {
            this.statusMessage.textContent = 'Stalemate!';
        } else {
            const currentTurn = document.querySelector('.piece')?.dataset.pieceType.startsWith('white') ? 'Black' : 'White';
            this.statusMessage.textContent = `${currentTurn}'s turn`;
        }
    }
    
    async resetGame() {
        try {
            await fetch('/reset_game', { method: 'POST' });
            this.clearSelection();
            this.initializeBoard();
            this.statusMessage.textContent = "White's turn";
        } catch (error) {
            console.error('Error resetting game:', error);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ChessGame();
});